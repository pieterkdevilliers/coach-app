from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.routes import call_types, extractions, queries, recordings, transcripts


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Tables are managed exclusively by Alembic migrations.
    yield


app = FastAPI(title="Coach App API", version="0.1.0", lifespan=lifespan)

app.include_router(call_types.router, prefix="/api")
app.include_router(recordings.router, prefix="/api")
app.include_router(transcripts.router, prefix="/api")
app.include_router(extractions.router, prefix="/api")
app.include_router(queries.router, prefix="/api")


@app.get("/health", tags=["health"])
async def health() -> dict[str, str]:
    return {"status": "ok"}
