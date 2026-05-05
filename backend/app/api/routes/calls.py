from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.config import settings
from app.core.database import get_db
from app.models.call import Call, CallStatus
from app.models.call_summary import CallSummary
from app.models.client import Client
from app.models.next_action_step import NextActionStep
from app.models.recording import Recording
from app.models.transcript import Transcript
from app.models.user import User
from app.schemas.call import (
    ActionStepInCall,
    CallCreate,
    CallListResponse,
    CallResponse,
    CallUpdate,
    RecordingInCall,
    SummaryInCall,
    TranscriptInCall,
)
from app.core import s3_client as s3
from app.schemas.call_summary import CallSummaryResponse, CallSummaryUpsert
from app.schemas.next_action_step import ActionStepCreate, ActionStepResponse, ActionStepUpdate
from app.schemas.recording import (
    PresignUploadRequest,
    PresignUploadResponse,
    RecordingConfirmRequest,
    RecordingConfirmResponse,
    RecordingResponse,
)
from app.schemas.transcript import TranscriptResponse, TranscriptUpsert

router = APIRouter(tags=["calls"])


async def _get_call_or_404(db: AsyncSession, call_id: UUID, business_id: UUID) -> Call:
    result = await db.execute(
        select(Call).where(Call.id == call_id, Call.business_id == business_id)
    )
    call = result.scalar_one_or_none()
    if not call:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Call not found")
    return call


async def _build_call_response(db: AsyncSession, call: Call) -> CallResponse:
    recording_row = (await db.execute(
        select(Recording).where(Recording.call_id == call.id)
    )).scalar_one_or_none()

    transcript_row = (await db.execute(
        select(Transcript).where(Transcript.call_id == call.id)
    )).scalar_one_or_none()

    summary_row = (await db.execute(
        select(CallSummary).where(CallSummary.call_id == call.id)
    )).scalar_one_or_none()

    steps = (await db.execute(
        select(NextActionStep)
        .where(NextActionStep.call_id == call.id)
        .order_by(NextActionStep.sort_order, NextActionStep.created_at)
    )).scalars().all()

    return CallResponse(
        id=call.id,
        business_id=call.business_id,
        client_id=call.client_id,
        call_type_id=call.call_type_id,
        created_by_id=call.created_by_id,
        title=call.title,
        called_at=call.called_at,
        duration_seconds=call.duration_seconds,
        notes=call.notes,
        status=call.status,
        created_at=call.created_at,
        updated_at=call.updated_at,
        recording=RecordingInCall.model_validate(recording_row) if recording_row else None,
        transcript=TranscriptInCall.model_validate(transcript_row) if transcript_row else None,
        summary=SummaryInCall.model_validate(summary_row) if summary_row else None,
        action_steps=[ActionStepInCall.model_validate(s) for s in steps],
    )


# ── Calls ──────────────────────────────────────────────────────────────────

@router.get("/clients/{client_id}/calls", response_model=list[CallListResponse])
async def list_calls(
    client_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[CallListResponse]:
    client = (await db.execute(
        select(Client).where(
            Client.id == client_id,
            Client.business_id == current_user.business_id,
            Client.is_active.is_(True),
        )
    )).scalar_one_or_none()
    if not client:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Client not found")

    calls = (await db.execute(
        select(Call)
        .where(Call.client_id == client_id, Call.business_id == current_user.business_id)
        .order_by(Call.called_at.desc())
    )).scalars().all()

    results = []
    for call in calls:
        has_recording = (await db.execute(
            select(func.count()).select_from(Recording).where(Recording.call_id == call.id)
        )).scalar_one() > 0
        has_transcript = (await db.execute(
            select(func.count()).select_from(Transcript).where(Transcript.call_id == call.id)
        )).scalar_one() > 0
        has_summary = (await db.execute(
            select(func.count()).select_from(CallSummary).where(CallSummary.call_id == call.id)
        )).scalar_one() > 0
        steps_total = (await db.execute(
            select(func.count()).select_from(NextActionStep).where(NextActionStep.call_id == call.id)
        )).scalar_one()
        steps_done = (await db.execute(
            select(func.count()).select_from(NextActionStep).where(
                NextActionStep.call_id == call.id, NextActionStep.is_complete.is_(True)
            )
        )).scalar_one()

        results.append(CallListResponse(
            id=call.id,
            call_type_id=call.call_type_id,
            title=call.title,
            called_at=call.called_at,
            status=call.status,
            has_recording=has_recording,
            has_transcript=has_transcript,
            has_summary=has_summary,
            action_steps_total=steps_total,
            action_steps_complete=steps_done,
        ))

    return results


@router.post(
    "/clients/{client_id}/calls",
    response_model=CallResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_call(
    client_id: UUID,
    payload: CallCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> CallResponse:
    client = (await db.execute(
        select(Client).where(
            Client.id == client_id,
            Client.business_id == current_user.business_id,
            Client.is_active.is_(True),
        )
    )).scalar_one_or_none()
    if not client:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Client not found")

    call = Call(
        business_id=current_user.business_id,
        client_id=client_id,
        created_by_id=current_user.id,
        **payload.model_dump(),
    )
    db.add(call)
    await db.commit()
    await db.refresh(call)
    return await _build_call_response(db, call)


@router.get("/calls/{call_id}", response_model=CallResponse)
async def get_call(
    call_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> CallResponse:
    call = await _get_call_or_404(db, call_id, current_user.business_id)
    return await _build_call_response(db, call)


@router.put("/calls/{call_id}", response_model=CallResponse)
async def update_call(
    call_id: UUID,
    payload: CallUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> CallResponse:
    call = await _get_call_or_404(db, call_id, current_user.business_id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(call, field, value)
    await db.commit()
    await db.refresh(call)
    return await _build_call_response(db, call)


@router.delete("/calls/{call_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_call(
    call_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    call = await _get_call_or_404(db, call_id, current_user.business_id)
    await db.delete(call)
    await db.commit()


# ── Recording ─────────────────────────────────────────────────────────────

@router.post("/calls/{call_id}/recording/presign", response_model=PresignUploadResponse)
async def presign_recording_upload(
    call_id: UUID,
    payload: PresignUploadRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> PresignUploadResponse:
    """Generate a pre-signed S3 PUT URL for direct browser-to-S3 upload."""
    call = await _get_call_or_404(db, call_id, current_user.business_id)

    existing = (await db.execute(
        select(Recording).where(Recording.call_id == call_id)
    )).scalar_one_or_none()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A recording is already attached to this call. Remove it first.",
        )

    s3_key = s3.build_s3_key(
        str(call.business_id), str(call_id), payload.file_name
    )
    upload_url = await s3.presign_upload(s3_key, payload.content_type)

    return PresignUploadResponse(
        upload_url=upload_url,
        s3_key=s3_key,
        expires_in=settings.aws_s3_upload_expires,
    )


@router.post(
    "/calls/{call_id}/recording/confirm",
    response_model=RecordingConfirmResponse,
    status_code=status.HTTP_201_CREATED,
)
async def confirm_recording_upload(
    call_id: UUID,
    payload: RecordingConfirmRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> RecordingConfirmResponse:
    """Called after the browser finishes the S3 upload. Saves the recording
    and returns a pre-signed GET URL for the Scribe API."""
    call = await _get_call_or_404(db, call_id, current_user.business_id)

    existing = (await db.execute(
        select(Recording).where(Recording.call_id == call_id)
    )).scalar_one_or_none()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Recording already confirmed for this call.",
        )

    recording = Recording(
        call_id=call_id,
        business_id=call.business_id,
        file_name=payload.file_name,
        s3_key=payload.s3_key,
    )
    db.add(recording)
    await db.commit()
    await db.refresh(recording)

    presigned_read_url = await s3.presign_read(payload.s3_key)

    return RecordingConfirmResponse(
        id=recording.id,
        call_id=recording.call_id,
        file_name=recording.file_name,
        s3_key=recording.s3_key,
        presigned_read_url=presigned_read_url,
        created_at=recording.created_at,
    )


@router.delete("/calls/{call_id}/recording", status_code=status.HTTP_204_NO_CONTENT)
async def remove_recording(
    call_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    await _get_call_or_404(db, call_id, current_user.business_id)
    recording = (await db.execute(
        select(Recording).where(Recording.call_id == call_id)
    )).scalar_one_or_none()
    if not recording:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No recording attached")
    await db.delete(recording)
    await db.commit()


# ── Transcript ────────────────────────────────────────────────────────────

@router.put("/calls/{call_id}/transcript", response_model=TranscriptResponse)
async def upsert_transcript(
    call_id: UUID,
    payload: TranscriptUpsert,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> TranscriptResponse:
    call = await _get_call_or_404(db, call_id, current_user.business_id)
    transcript = (await db.execute(
        select(Transcript).where(Transcript.call_id == call_id)
    )).scalar_one_or_none()

    word_count = len(payload.content.split())
    if transcript:
        transcript.content = payload.content
        transcript.word_count = word_count
    else:
        transcript = Transcript(
            call_id=call_id,
            business_id=call.business_id,
            content=payload.content,
            word_count=word_count,
        )
        db.add(transcript)

    await db.commit()
    await db.refresh(transcript)
    return TranscriptResponse.model_validate(transcript)


@router.delete("/calls/{call_id}/transcript", status_code=status.HTTP_204_NO_CONTENT)
async def delete_transcript(
    call_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    await _get_call_or_404(db, call_id, current_user.business_id)
    transcript = (await db.execute(
        select(Transcript).where(Transcript.call_id == call_id)
    )).scalar_one_or_none()
    if not transcript:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No transcript")
    await db.delete(transcript)
    await db.commit()


# ── Summary ───────────────────────────────────────────────────────────────

@router.put("/calls/{call_id}/summary", response_model=CallSummaryResponse)
async def upsert_summary(
    call_id: UUID,
    payload: CallSummaryUpsert,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> CallSummaryResponse:
    call = await _get_call_or_404(db, call_id, current_user.business_id)
    summary = (await db.execute(
        select(CallSummary).where(CallSummary.call_id == call_id)
    )).scalar_one_or_none()

    if summary:
        summary.content = payload.content
    else:
        summary = CallSummary(
            call_id=call_id,
            business_id=call.business_id,
            content=payload.content,
        )
        db.add(summary)

    await db.commit()
    await db.refresh(summary)
    return CallSummaryResponse.model_validate(summary)


@router.delete("/calls/{call_id}/summary", status_code=status.HTTP_204_NO_CONTENT)
async def delete_summary(
    call_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    await _get_call_or_404(db, call_id, current_user.business_id)
    summary = (await db.execute(
        select(CallSummary).where(CallSummary.call_id == call_id)
    )).scalar_one_or_none()
    if not summary:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No summary")
    await db.delete(summary)
    await db.commit()


# ── Action Steps ─────────────────────────────────────────────────────────

@router.post(
    "/calls/{call_id}/action-steps",
    response_model=ActionStepResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_action_step(
    call_id: UUID,
    payload: ActionStepCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ActionStepResponse:
    call = await _get_call_or_404(db, call_id, current_user.business_id)
    step = NextActionStep(
        call_id=call_id,
        business_id=call.business_id,
        **payload.model_dump(),
    )
    db.add(step)
    await db.commit()
    await db.refresh(step)
    return ActionStepResponse.model_validate(step)


@router.put("/calls/{call_id}/action-steps/{step_id}", response_model=ActionStepResponse)
async def update_action_step(
    call_id: UUID,
    step_id: UUID,
    payload: ActionStepUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ActionStepResponse:
    await _get_call_or_404(db, call_id, current_user.business_id)
    step = (await db.execute(
        select(NextActionStep).where(
            NextActionStep.id == step_id,
            NextActionStep.call_id == call_id,
            NextActionStep.business_id == current_user.business_id,
        )
    )).scalar_one_or_none()
    if not step:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Action step not found")

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(step, field, value)
    await db.commit()
    await db.refresh(step)
    return ActionStepResponse.model_validate(step)


@router.delete("/calls/{call_id}/action-steps/{step_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_action_step(
    call_id: UUID,
    step_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    await _get_call_or_404(db, call_id, current_user.business_id)
    step = (await db.execute(
        select(NextActionStep).where(
            NextActionStep.id == step_id,
            NextActionStep.call_id == call_id,
            NextActionStep.business_id == current_user.business_id,
        )
    )).scalar_one_or_none()
    if not step:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Action step not found")
    await db.delete(step)
    await db.commit()
