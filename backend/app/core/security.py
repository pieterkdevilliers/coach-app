import base64
import hashlib
import uuid
from datetime import datetime, timedelta, timezone

import bcrypt
import jwt

from app.core.config import settings

_ALGORITHM = "HS256"


def _normalise(password: str) -> bytes:
    # SHA-256 → base64 keeps any-length password within bcrypt's 72-byte limit.
    return base64.b64encode(hashlib.sha256(password.encode()).digest())


def hash_password(password: str) -> str:
    return bcrypt.hashpw(_normalise(password), bcrypt.gensalt()).decode()


def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(_normalise(plain), hashed.encode())


def create_access_token(user_id: uuid.UUID, business_id: uuid.UUID, role: str) -> str:
    payload = {
        "sub": str(user_id),
        "business_id": str(business_id),
        "role": role,
        "type": "access",
        "iat": datetime.now(timezone.utc),
        "exp": datetime.now(timezone.utc)
        + timedelta(minutes=settings.jwt_access_token_expire_minutes),
    }
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=_ALGORITHM)


def create_refresh_token(user_id: uuid.UUID) -> str:
    payload = {
        "sub": str(user_id),
        "type": "refresh",
        "iat": datetime.now(timezone.utc),
        "exp": datetime.now(timezone.utc)
        + timedelta(days=settings.jwt_refresh_token_expire_days),
    }
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=_ALGORITHM)


def decode_token(token: str) -> dict:
    return jwt.decode(token, settings.jwt_secret_key, algorithms=[_ALGORITHM])
