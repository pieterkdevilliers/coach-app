from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.user import User
from app.schemas.auth import (
    AcceptInviteRequest,
    LoginRequest,
    RefreshRequest,
    RegisterRequest,
    TokenResponse,
)
from app.schemas.user import MeResponse
from app.services import auth as auth_service

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(payload: RegisterRequest, db: AsyncSession = Depends(get_db)) -> TokenResponse:
    try:
        return await auth_service.register(db, payload)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))


@router.post("/login", response_model=TokenResponse)
async def login(payload: LoginRequest, db: AsyncSession = Depends(get_db)) -> TokenResponse:
    try:
        return await auth_service.login(db, payload)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc))


@router.post("/refresh", response_model=TokenResponse)
async def refresh(payload: RefreshRequest, db: AsyncSession = Depends(get_db)) -> TokenResponse:
    try:
        return await auth_service.refresh(db, payload.refresh_token)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc))


@router.post("/accept-invite", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def accept_invite(
    payload: AcceptInviteRequest, db: AsyncSession = Depends(get_db)
) -> TokenResponse:
    try:
        return await auth_service.accept_invite(db, payload)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))


@router.get("/me", response_model=MeResponse)
async def me(current_user: User = Depends(get_current_user)) -> MeResponse:
    return MeResponse.model_validate(current_user)
