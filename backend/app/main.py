from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.services import scribe as scribe_service
from app.api.routes import (
    auth,
    call_types,
    calls,
    client_notes,
    clients,
    invitations,
    users,
)


@asynccontextmanager
async def lifespan(_app: FastAPI):
    # Re-launch polling for any calls that were still processing on last shutdown.
    # Wrapped so a DB hiccup at startup never prevents the app from serving requests.
    try:
        await scribe_service.restart_pending()
    except Exception as exc:
        import logging
        logging.getLogger(__name__).warning("restart_pending failed at startup: %s", exc)
    yield


app = FastAPI(title="Coach App API", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api")
app.include_router(clients.router, prefix="/api")
app.include_router(client_notes.router, prefix="/api")
app.include_router(users.router, prefix="/api")
app.include_router(invitations.router, prefix="/api")
app.include_router(call_types.router, prefix="/api")
app.include_router(calls.router, prefix="/api")


@app.get("/health", tags=["health"])
async def health() -> dict[str, str]:
    return {"status": "ok"}
