from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import require_owner
from app.core.database import get_db
from app.models.invitation import Invitation
from app.models.user import User
from app.schemas.invitation import InvitationCreate, InvitationResponse
from app.services import auth as auth_service

router = APIRouter(prefix="/invitations", tags=["invitations"])


@router.post("", response_model=InvitationResponse, status_code=status.HTTP_201_CREATED)
async def create_invitation(
    payload: InvitationCreate,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_owner),
) -> InvitationResponse:
    frontend_base = str(request.base_url).rstrip("/")
    invitation = await auth_service.create_invitation(
        db,
        business_id=current_user.business_id,
        invited_by_id=current_user.id,
        email=payload.email,
        frontend_base_url=frontend_base,
    )
    response = InvitationResponse.model_validate(invitation)
    response.invite_url = f"{frontend_base}/auth/accept-invite?token={invitation.token}"
    return response


@router.get("", response_model=list[InvitationResponse])
async def list_invitations(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_owner),
) -> list[InvitationResponse]:
    result = await db.execute(
        select(Invitation)
        .where(
            Invitation.business_id == current_user.business_id,
            Invitation.accepted_at.is_(None),
        )
        .order_by(Invitation.created_at.desc())
    )
    return [InvitationResponse.model_validate(i) for i in result.scalars().all()]


@router.delete("/{invitation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def revoke_invitation(
    invitation_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_owner),
) -> None:
    invitation = await db.get(Invitation, invitation_id)
    if not invitation or invitation.business_id != current_user.business_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invitation not found")
    if invitation.accepted_at is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invitation already accepted"
        )
    await db.delete(invitation)
    await db.commit()
