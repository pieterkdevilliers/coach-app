from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.client import Client
from app.models.client_note import ClientNote
from app.models.user import User
from app.schemas.client_note import ClientNoteCreate, ClientNoteResponse

router = APIRouter(prefix="/clients", tags=["client-notes"])


async def _assert_client_access(
    db: AsyncSession, client_id: UUID, business_id: UUID
) -> None:
    result = await db.execute(
        select(Client).where(
            Client.id == client_id,
            Client.business_id == business_id,
            Client.is_active.is_(True),
        )
    )
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Client not found")


@router.get("/{client_id}/notes", response_model=list[ClientNoteResponse])
async def list_notes(
    client_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[ClientNoteResponse]:
    await _assert_client_access(db, client_id, current_user.business_id)

    result = await db.execute(
        select(ClientNote, User.full_name)
        .join(User, ClientNote.created_by_id == User.id)
        .where(
            ClientNote.client_id == client_id,
            ClientNote.business_id == current_user.business_id,
        )
        .order_by(ClientNote.created_at.desc())
    )
    rows = result.all()
    return [
        ClientNoteResponse(
            id=note.id,
            client_id=note.client_id,
            business_id=note.business_id,
            created_by_id=note.created_by_id,
            created_by_name=full_name,
            content=note.content,
            created_at=note.created_at,
        )
        for note, full_name in rows
    ]


@router.post(
    "/{client_id}/notes",
    response_model=ClientNoteResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_note(
    client_id: UUID,
    payload: ClientNoteCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ClientNoteResponse:
    await _assert_client_access(db, client_id, current_user.business_id)

    note = ClientNote(
        client_id=client_id,
        business_id=current_user.business_id,
        created_by_id=current_user.id,
        content=payload.content,
    )
    db.add(note)
    await db.commit()
    await db.refresh(note)

    return ClientNoteResponse(
        id=note.id,
        client_id=note.client_id,
        business_id=note.business_id,
        created_by_id=note.created_by_id,
        created_by_name=current_user.full_name,
        content=note.content,
        created_at=note.created_at,
    )


@router.delete("/{client_id}/notes/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_note(
    client_id: UUID,
    note_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    result = await db.execute(
        select(ClientNote).where(
            ClientNote.id == note_id,
            ClientNote.client_id == client_id,
            ClientNote.business_id == current_user.business_id,
        )
    )
    note = result.scalar_one_or_none()
    if not note:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note not found")

    await db.delete(note)
    await db.commit()
