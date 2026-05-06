"""Scribe API integration — submission, background polling, result persistence."""

import asyncio
import json
import logging
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import s3_client as s3
from app.core.config import settings
from app.core.database import AsyncSessionLocal
from app.core.scribe_client import scribe_client
from app.models.call import Call, CallStatus
from app.models.call_summary import CallSummary
from app.models.call_type import CallType
from app.models.next_action_step import NextActionStep
from app.models.recording import Recording
from app.models.transcript import Transcript

logger = logging.getLogger(__name__)

# Keys searched (in order) for action step arrays inside the extraction JSON.
_ACTION_STEP_KEYS = [
    "next_actions",
    "next_action_steps",
    "action_steps",
    "action_items",
    "recommended_actions",
    "actions",
    "commitments",
]


async def submit(db: AsyncSession, call_id: UUID, business_id: UUID) -> str:
    """
    Validate, build the Scribe request, submit it, persist the job_id, flip the
    call to `processing`, and fire off the background polling task.
    Returns the job_id.
    """
    call = (await db.execute(
        select(Call).where(Call.id == call_id, Call.business_id == business_id)
    )).scalar_one_or_none()
    if not call:
        raise ValueError("Call not found")

    recording = (await db.execute(
        select(Recording).where(Recording.call_id == call_id)
    )).scalar_one_or_none()
    if not recording or not recording.s3_key:
        raise ValueError("No recording with an S3 key attached to this call")

    call_type = await db.get(CallType, call.call_type_id)
    if not call_type:
        raise ValueError("Call type not found")

    presigned_url = await s3.presign_read(recording.s3_key)

    job_id = await scribe_client.process_url(
        s3_url=presigned_url,
        prompt=call_type.prompt_template,
    )

    recording.scribe_job_id = job_id
    call.status = CallStatus.processing
    await db.commit()

    asyncio.create_task(_poll_and_save(call_id, job_id))
    logger.info("Scribe job %s started for call %s", job_id, call_id)
    return job_id


async def _poll_and_save(call_id: UUID, job_id: str) -> None:
    """Background task: poll until terminal state, then persist results."""
    interval = settings.scribe_poll_interval_seconds
    logger.info("Polling job %s every %ss", job_id, interval)

    while True:
        await asyncio.sleep(interval)

        try:
            result = await scribe_client.get_job(job_id)
        except Exception as exc:
            logger.warning("Poll error for job %s: %s — retrying", job_id, exc)
            continue

        status = result.get("status")
        logger.debug("Job %s status=%s", job_id, status)

        if status not in ("complete", "failed"):
            continue

        async with AsyncSessionLocal() as db:
            call = await db.get(Call, call_id)
            if not call:
                logger.error("Call %s vanished — stopping poll for job %s", call_id, job_id)
                return

            if status == "complete":
                await _persist_results(db, call, result)
                logger.info("Job %s complete — results saved for call %s", job_id, call_id)
            else:
                call.status = CallStatus.failed
                recording = (await db.execute(
                    select(Recording).where(Recording.call_id == call_id)
                )).scalar_one_or_none()
                if recording:
                    recording.error_message = result.get("error") or "Scribe processing failed"
                await db.commit()
                logger.warning("Job %s failed for call %s: %s", job_id, call_id, result.get("error"))

        return


def _normalise_extraction(raw) -> tuple[str, dict | None]:
    """
    Scribe may return `extraction` as a string, a dict, or a markdown-fenced
    JSON block.  Returns (storage_string, parsed_dict_or_None).
    """
    if raw is None:
        return "", None

    # Already a dict — Scribe parsed the JSON for us
    if isinstance(raw, dict):
        return json.dumps(raw, indent=2, ensure_ascii=False), raw

    if not isinstance(raw, str) or not raw.strip():
        return str(raw), None

    text = raw.strip()

    # Strip markdown code fences (```json ... ``` or ``` ... ```)
    if text.startswith("```"):
        lines = text.splitlines()
        start = 1  # skip the opening fence line
        end = len(lines) - 1 if lines[-1].strip() == "```" else len(lines)
        text = "\n".join(lines[start:end]).strip()

    try:
        parsed = json.loads(text)
        if isinstance(parsed, dict):
            return json.dumps(parsed, indent=2, ensure_ascii=False), parsed
    except (json.JSONDecodeError, ValueError):
        pass

    # Not valid JSON — store as plain text, no structured parsing
    return text, None


async def _persist_results(db: AsyncSession, call: Call, job_result: dict) -> None:
    """Save transcript, summary, and action steps from a completed Scribe job."""
    transcript_text: str = job_result.get("transcript") or ""
    extraction_storage, extraction_dict = _normalise_extraction(job_result.get("extraction"))

    # ── Transcript ────────────────────────────────────────────────────────
    if transcript_text:
        existing = (await db.execute(
            select(Transcript).where(Transcript.call_id == call.id)
        )).scalar_one_or_none()

        if existing:
            existing.content = transcript_text
            existing.word_count = len(transcript_text.split())
        else:
            db.add(Transcript(
                call_id=call.id,
                business_id=call.business_id,
                content=transcript_text,
                word_count=len(transcript_text.split()),
            ))

    # ── Summary (full extraction) ─────────────────────────────────────────
    if extraction_storage:
        existing_summary = (await db.execute(
            select(CallSummary).where(CallSummary.call_id == call.id)
        )).scalar_one_or_none()

        if existing_summary:
            existing_summary.content = extraction_storage
        else:
            db.add(CallSummary(
                call_id=call.id,
                business_id=call.business_id,
                content=extraction_storage,
            ))

        if extraction_dict:
            await _parse_and_save_action_steps(db, call, extraction_dict)

    call.status = CallStatus.complete
    await db.commit()


async def _parse_and_save_action_steps(
    db: AsyncSession, call: Call, data: dict
) -> None:
    """
    Extract action step items from the parsed extraction dict and persist them.
    Handles {action, owner, deadline} objects as well as plain strings.
    """
    steps: list[str] = []
    for key in _ACTION_STEP_KEYS:
        value = data.get(key)
        if not value:
            continue
        if isinstance(value, list):
            for item in value:
                if isinstance(item, dict):
                    action = (
                        item.get("action")
                        or item.get("description")
                        or item.get("task")
                        or ""
                    )
                    if not action:
                        continue
                    owner = item.get("owner", "")
                    deadline = item.get("deadline", "")
                    parts = [action.strip()]
                    if owner:
                        parts.append(f"Owner: {owner}")
                    if deadline:
                        parts.append(f"Deadline: {deadline}")
                    steps.append(" | ".join(parts))
                elif isinstance(item, str) and item.strip():
                    steps.append(item.strip())
        elif isinstance(value, str) and value.strip():
            steps.append(value.strip())

        if steps:
            break  # Use the first matching key only

    if not steps:
        return

    for order, description in enumerate(steps):
        db.add(NextActionStep(
            call_id=call.id,
            business_id=call.business_id,
            description=description,
            sort_order=order,
        ))


async def restart_pending() -> None:
    """
    Called at startup: re-launch polling tasks for any calls that were still
    `processing` when the server last stopped.
    """
    async with AsyncSessionLocal() as db:
        rows = (await db.execute(
            select(Recording.scribe_job_id, Recording.call_id)
            .join(Call, Call.id == Recording.call_id)
            .where(
                Call.status == CallStatus.processing,
                Recording.scribe_job_id.is_not(None),
            )
        )).all()

    for job_id, call_id in rows:
        logger.info("Restarting poll for call %s job %s", call_id, job_id)
        asyncio.create_task(_poll_and_save(call_id, job_id))
