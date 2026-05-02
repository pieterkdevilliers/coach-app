"""Scribe API job dispatch and polling."""

import asyncio
import logging
from typing import Any

from app.core.config import settings
from app.core.scribe_client import scribe_client

logger = logging.getLogger(__name__)


async def dispatch_process_file(
    file_bytes: bytes,
    filename: str,
    prompt: str,
) -> str:
    """Upload a file to Scribe API and return the job_id."""
    return await scribe_client.process_file(file_bytes, filename, prompt)


async def dispatch_extract(transcript: str, prompt: str) -> str:
    """Submit an ad-hoc extraction and return the job_id."""
    return await scribe_client.extract(transcript, prompt)


async def poll_until_complete(job_id: str) -> dict[str, Any]:
    """
    Poll Scribe API every SCRIBE_POLL_INTERVAL_SECONDS until the job reaches
    a terminal state (complete or failed).  Never times out — caller is
    responsible for deciding when to give up.
    """
    interval = settings.scribe_poll_interval_seconds
    while True:
        result = await scribe_client.get_job(job_id)
        status = result.get("status")
        if status in ("complete", "failed"):
            return result
        logger.debug("Job %s status=%s, polling again in %ss", job_id, status, interval)
        await asyncio.sleep(interval)
