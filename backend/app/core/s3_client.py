import asyncio
from functools import partial

import boto3
from botocore.config import Config
from botocore.exceptions import BotoCoreError, ClientError
from fastapi import HTTPException, status

from app.core.config import settings


def _assert_configured() -> None:
    if not settings.aws_access_key_id or not settings.aws_secret_access_key or not settings.aws_s3_bucket:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="AWS S3 is not configured on this server.",
        )


def _client():
    return boto3.client(
        "s3",
        region_name=settings.aws_region,
        aws_access_key_id=settings.aws_access_key_id,
        aws_secret_access_key=settings.aws_secret_access_key,
        config=Config(signature_version="s3v4"),
    )


def build_s3_key(business_id: str, call_id: str, filename: str) -> str:
    return f"recordings/{business_id}/{call_id}/{filename}"


def _sync_presign_upload(s3_key: str, content_type: str) -> str:
    return _client().generate_presigned_url(
        "put_object",
        Params={
            "Bucket": settings.aws_s3_bucket,
            "Key": s3_key,
            "ContentType": content_type,
        },
        ExpiresIn=settings.aws_s3_upload_expires,
    )


def _sync_presign_read(s3_key: str) -> str:
    return _client().generate_presigned_url(
        "get_object",
        Params={
            "Bucket": settings.aws_s3_bucket,
            "Key": s3_key,
        },
        ExpiresIn=settings.aws_s3_read_expires,
    )


async def presign_upload(s3_key: str, content_type: str) -> str:
    """Return a pre-signed PUT URL for direct browser-to-S3 upload."""
    _assert_configured()
    try:
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None, partial(_sync_presign_upload, s3_key, content_type)
        )
    except (BotoCoreError, ClientError) as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Failed to generate upload URL: {exc}",
        ) from exc


async def presign_read(s3_key: str) -> str:
    """Return a pre-signed GET URL for reading the object (e.g. Scribe API)."""
    _assert_configured()
    try:
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None, partial(_sync_presign_read, s3_key)
        )
    except (BotoCoreError, ClientError) as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Failed to generate read URL: {exc}",
        ) from exc
