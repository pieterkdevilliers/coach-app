import secrets
import uuid
from datetime import datetime, timedelta, timezone

import jwt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.models.business import Business
from app.models.call_type import CallType
from app.models.invitation import Invitation
from app.models.user import User, UserRole
from app.schemas.auth import (
    AcceptInviteRequest,
    LoginRequest,
    RegisterRequest,
    TokenResponse,
)

_DEFAULT_CALL_TYPES = [
    {
        "name": "Quick 15 Min Call",
        "prompt_template": (
            "Extract the following from this short call transcript: main topic discussed, "
            "any actions agreed, any follow-up required, and key concerns raised by the client. "
            "Return as structured JSON."
        ),
    },
    {
        "name": "90-Min Audit Call",
        "prompt_template": (
            "This is a business audit call. Extract: the business overview provided, "
            "key challenges identified, current tools and processes mentioned, opportunities "
            "discussed, recommended actions, and any commitments made. Return as structured JSON."
        ),
    },
    {
        "name": "Coaching Client Call",
        "prompt_template": (
            "This is a coaching session. Extract: the client's stated goals for this session, "
            "key insights or breakthroughs, action items agreed, homework or tasks set, and progress "
            "noted against previous goals. Return as structured JSON."
        ),
    },
    {
        "name": "Full Day Workshop",
        "prompt_template": (
            "This is a full day workshop recording. Extract: the workshop objectives, "
            "key topics covered in each session, participant questions or discussion themes, "
            "decisions made, action items with owners if mentioned, and overall outcomes. "
            "Return as structured JSON."
        ),
    },
]


async def _email_taken(db: AsyncSession, email: str) -> bool:
    result = await db.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none() is not None


async def register(db: AsyncSession, payload: RegisterRequest) -> TokenResponse:
    if await _email_taken(db, payload.email):
        raise ValueError("Email already registered")

    business = Business(name=payload.business_name, email=payload.business_email)
    db.add(business)
    await db.flush()

    owner = User(
        business_id=business.id,
        email=payload.email,
        full_name=payload.full_name,
        hashed_password=hash_password(payload.password),
        role=UserRole.owner,
    )
    db.add(owner)

    for ct in _DEFAULT_CALL_TYPES:
        db.add(CallType(business_id=business.id, **ct))

    await db.commit()
    await db.refresh(owner)

    return TokenResponse(
        access_token=create_access_token(owner.id, business.id, owner.role),
        refresh_token=create_refresh_token(owner.id),
    )


async def login(db: AsyncSession, payload: LoginRequest) -> TokenResponse:
    result = await db.execute(select(User).where(User.email == payload.email))
    user = result.scalar_one_or_none()

    if not user or not user.is_active or not verify_password(payload.password, user.hashed_password):
        raise ValueError("Invalid credentials")

    return TokenResponse(
        access_token=create_access_token(user.id, user.business_id, user.role),
        refresh_token=create_refresh_token(user.id),
    )


async def refresh(db: AsyncSession, refresh_token: str) -> TokenResponse:
    try:
        payload = decode_token(refresh_token)
    except jwt.InvalidTokenError:
        raise ValueError("Invalid refresh token")

    if payload.get("type") != "refresh":
        raise ValueError("Invalid token type")

    user = await db.get(User, uuid.UUID(payload["sub"]))
    if not user or not user.is_active:
        raise ValueError("User not found or inactive")

    return TokenResponse(
        access_token=create_access_token(user.id, user.business_id, user.role),
        refresh_token=create_refresh_token(user.id),
    )


async def create_invitation(
    db: AsyncSession,
    business_id: uuid.UUID,
    invited_by_id: uuid.UUID,
    email: str,
    frontend_base_url: str,
) -> Invitation:
    token = secrets.token_urlsafe(32)
    expires_at = datetime.now(timezone.utc) + timedelta(days=settings.invite_token_expire_days)

    invitation = Invitation(
        business_id=business_id,
        invited_by_id=invited_by_id,
        email=email,
        token=token,
        expires_at=expires_at,
    )
    db.add(invitation)
    await db.commit()
    await db.refresh(invitation)
    return invitation


async def accept_invite(db: AsyncSession, payload: AcceptInviteRequest) -> TokenResponse:
    result = await db.execute(
        select(Invitation).where(Invitation.token == payload.token)
    )
    invitation = result.scalar_one_or_none()

    if not invitation:
        raise ValueError("Invalid invite token")
    if invitation.accepted_at is not None:
        raise ValueError("Invite already used")
    if invitation.expires_at < datetime.now(timezone.utc):
        raise ValueError("Invite has expired")

    if await _email_taken(db, invitation.email):
        raise ValueError("Email already registered")

    user = User(
        business_id=invitation.business_id,
        email=invitation.email,
        full_name=payload.full_name,
        hashed_password=hash_password(payload.password),
        role=UserRole.coach,
    )
    db.add(user)

    invitation.accepted_at = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(user)

    return TokenResponse(
        access_token=create_access_token(user.id, user.business_id, user.role),
        refresh_token=create_refresh_token(user.id),
    )
