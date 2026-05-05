from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.api.routes import (
    auth,
    call_types,
    client_notes,
    clients,
    extractions,
    invitations,
    queries,
    recordings,
    transcripts,
    users,
)


@asynccontextmanager
async def lifespan(_app: FastAPI):
    # Tables are managed exclusively by Alembic migrations.
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
app.include_router(recordings.router, prefix="/api")
app.include_router(transcripts.router, prefix="/api")
app.include_router(extractions.router, prefix="/api")
app.include_router(queries.router, prefix="/api")


@app.get("/health", tags=["health"])
async def health() -> dict[str, str]:
    return {"status": "ok"}
