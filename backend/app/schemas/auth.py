from pydantic import EmailStr

from app.schemas._base import CamelSchema


class RegisterRequest(CamelSchema):
    business_name: str
    business_email: EmailStr
    full_name: str
    email: EmailStr
    password: str


class LoginRequest(CamelSchema):
    email: EmailStr
    password: str


class TokenResponse(CamelSchema):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshRequest(CamelSchema):
    refresh_token: str


class AcceptInviteRequest(CamelSchema):
    token: str
    full_name: str
    password: str
