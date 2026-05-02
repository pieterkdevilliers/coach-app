from typing import Any

import httpx

from app.core.config import settings


class ScribeClient:
    """Thin httpx wrapper for Scribe API communication."""

    def __init__(self) -> None:
        self._base_url = settings.scribe_api_url
        self._headers = {"X-API-Key": settings.scribe_api_key}

    def _client(self) -> httpx.AsyncClient:
        return httpx.AsyncClient(
            base_url=self._base_url,
            headers=self._headers,
            timeout=60.0,
        )

    async def health(self) -> dict[str, Any]:
        async with self._client() as client:
            response = await client.get("/health")
            response.raise_for_status()
            return response.json()

    async def process_file(
        self,
        file_bytes: bytes,
        filename: str,
        prompt: str,
        language: str = "en",
    ) -> str:
        async with self._client() as client:
            response = await client.post(
                "/process",
                files={"file": (filename, file_bytes)},
                data={"prompt": prompt, "language": language},
            )
            response.raise_for_status()
            return response.json()["job_id"]

    async def process_url(self, s3_url: str, prompt: str, language: str = "en") -> str:
        async with self._client() as client:
            response = await client.post(
                "/process-url",
                json={"s3_url": s3_url, "prompt": prompt, "language": language},
            )
            response.raise_for_status()
            return response.json()["job_id"]

    async def extract(self, transcript: str, prompt: str) -> str:
        async with self._client() as client:
            response = await client.post(
                "/extract",
                json={"transcript": transcript, "prompt": prompt},
            )
            response.raise_for_status()
            return response.json()["job_id"]

    async def get_job(self, job_id: str) -> dict[str, Any]:
        async with self._client() as client:
            response = await client.get(f"/job/{job_id}")
            response.raise_for_status()
            return response.json()


scribe_client = ScribeClient()
