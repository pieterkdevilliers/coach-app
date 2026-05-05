from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.client import Client
from app.models.user import User
from app.schemas.client import ClientCreate, ClientResponse, ClientUpdate

router = APIRouter(prefix="/clients", tags=["clients"])


async def _get_client_or_404(db: AsyncSession, client_id: UUID, business_id: UUID) -> Client:
    result = await db.execute(
        select(Client).where(
            Client.id == client_id,
            Client.business_id == business_id,
            Client.is_active.is_(True),
        )
    )
    client = result.scalar_one_or_none()
    if not client:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Client not found")
    return client


@router.get("", response_model=list[ClientResponse])
async def list_clients(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[ClientResponse]:
    result = await db.execute(
        select(Client).where(
            Client.business_id == current_user.business_id,
            Client.is_active.is_(True),
        ).order_by(Client.full_name)
    )
    return [ClientResponse.model_validate(c) for c in result.scalars().all()]


@router.post("", response_model=ClientResponse, status_code=status.HTTP_201_CREATED)
async def create_client(
    payload: ClientCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ClientResponse:
    client = Client(
        business_id=current_user.business_id,
        created_by_id=current_user.id,
        **payload.model_dump(),
    )
    db.add(client)
    await db.commit()
    await db.refresh(client)
    return ClientResponse.model_validate(client)


@router.get("/{client_id}", response_model=ClientResponse)
async def get_client(
    client_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ClientResponse:
    client = await _get_client_or_404(db, client_id, current_user.business_id)
    return ClientResponse.model_validate(client)


@router.put("/{client_id}", response_model=ClientResponse)
async def update_client(
    client_id: UUID,
    payload: ClientUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ClientResponse:
    client = await _get_client_or_404(db, client_id, current_user.business_id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(client, field, value)
    await db.commit()
    await db.refresh(client)
    return ClientResponse.model_validate(client)


@router.delete("/{client_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_client(
    client_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    client = await _get_client_or_404(db, client_id, current_user.business_id)
    client.is_active = False
    await db.commit()
