# Coach App — CLAUDE.md

## Project Overview
Coach App is the product-facing application for a business coach and adviser. It allows the user
to upload recordings of client calls, assign them to a call type, trigger transcription and
extraction via the Scribe API (a separate local service), review results, and run ad-hoc queries
against transcripts.

It consists of a FastAPI backend and a Nuxt 3 frontend, backed by a Postgres database.

---

## Tech Stack

### Backend
- **Runtime:** Python 3.12
- **Framework:** FastAPI — do not use Flask, Django, or any other framework
- **Validation:** Pydantic v2 for all data models and type hints
- **ORM:** SQLAlchemy 2.x (async) + Alembic for migrations
- **AI Orchestration:** Pydantic-AI (for any direct LLM calls)
- **HTTP Client:** httpx (for Scribe API communication)
- **Database:** PostgreSQL 16

### Frontend
- **Framework:** Nuxt 3 with Vue Composition API — do not use React, Angular, or other alternatives
- **Language:** TypeScript
- **Styling:** Tailwind CSS
- **State:** Pinia
- **HTTP:** useFetch / $fetch (Nuxt built-ins) — no direct DOM manipulation, use Vue directives

### Infrastructure
- Docker + Docker Compose
- Scribe API runs as a separate service (see scribe-api repo)

---

## Python Environment & Package Management
- **Use uv exclusively** for all Python-related tasks in this project.
- **Never** use pip, venv, virtualenv, poetry, conda, or requirements.txt directly.
- Manage dependencies via `pyproject.toml` + `uv.lock`.
- Key uv commands to prefer:
  - `uv add <package>` — to add dependencies (automatically updates pyproject.toml and uv.lock)
  - `uv add --dev <package>` — for development/test tools (e.g., pytest, ruff)
  - `uv sync` — to install/sync all dependencies from uv.lock
  - `uv run <command>` — to run scripts, tests, or the app inside the project environment
  - `uv run fastapi dev app/main.py` — to run the FastAPI app in development
  - `uv run --with <package> <command>` — for one-off tools without permanent installation
  - `uv tool install <tool>` — for globally available CLI tools if needed (rare in this project)
- When suggesting or executing installation steps, always write them as uv commands.
- For scripts/tests/linters: always wrap with `uv run` (e.g., `uv run ruff check .`, `uv run pytest`).
- If the project does not yet have pyproject.toml or uv.lock, initialise with `uv init`.
- When adding new packages, explicitly propose the `uv add` command and wait for confirmation.

---

## Key Design Principles
- The Coach App owns all business logic and data. Scribe API is a dumb processing service.
- Call Types define the extraction behaviour — the Coach App resolves the prompt template and
  sends it to Scribe API. Scribe API never sees call type names or IDs.
- All processing is async — the app polls Scribe API for job results and updates recording
  status accordingly via a background polling task.
- Single user for now — no multi-tenancy. Auth is a simple API key on the backend.
- Accuracy of extracted data matters more than processing speed.

---

## Architecture

### Backend
- Organise routes by feature in FastAPI
- Use dependency injection for services
- All data models must use Pydantic v2
- Use `async def` and `await` for all I/O-bound operations — no blocking calls on the main thread
- Follow PEP 8 for all Python code
- Use `snake_case` throughout the backend

### Frontend
- Pages in `pages/` directory via Nuxt
- Components in `components/`, prefixed by domain (e.g. `RecordingCard.vue`, `CallTypeForm.vue`)
- API calls handled with `useFetch` or composables — no axios
- No direct DOM manipulation — use Vue directives
- Use `camelCase` throughout the frontend
- Follow Airbnb style for TypeScript

---

## Project Structure

```
coach-app/
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── api/
│   │   │   └── routes/
│   │   │       ├── call_types.py
│   │   │       ├── recordings.py
│   │   │       ├── transcripts.py
│   │   │       ├── extractions.py
│   │   │       └── queries.py
│   │   ├── core/
│   │   │   ├── config.py
│   │   │   ├── database.py
│   │   │   └── scribe_client.py   # httpx client for Scribe API
│   │   ├── models/                # SQLAlchemy models
│   │   │   ├── call_type.py
│   │   │   ├── recording.py
│   │   │   ├── transcript.py
│   │   │   ├── extraction.py
│   │   │   └── query.py
│   │   ├── schemas/               # Pydantic v2 request/response schemas
│   │   │   ├── call_type.py
│   │   │   ├── recording.py
│   │   │   ├── transcript.py
│   │   │   ├── extraction.py
│   │   │   └── query.py
│   │   └── services/
│   │       ├── scribe.py          # Scribe API job dispatch and polling
│   │       └── recordings.py      # Recording processing orchestration
│   ├── alembic/
│   ├── pyproject.toml             # All dependencies and config managed here
│   ├── uv.lock
│   └── .env.example
├── frontend/
│   ├── pages/
│   │   ├── index.vue              # Dashboard / recent recordings
│   │   ├── recordings/
│   │   │   ├── index.vue          # Recordings list
│   │   │   ├── [id].vue           # Recording detail (transcript, extraction, queries)
│   │   │   └── upload.vue         # Upload new recording
│   │   └── settings/
│   │       └── call-types.vue     # Call Type CRUD
│   ├── components/
│   ├── stores/                    # Pinia stores
│   ├── composables/
│   └── nuxt.config.ts
└── docker-compose.yml
```

---

## Data Models

### CallType
```python
class CallType(Base):
    id: UUID
    name: str                    # e.g. "Quick 15 Min", "90-Min Audit"
    description: str | None
    prompt_template: str         # The extraction prompt sent to Scribe API
    is_active: bool = True
    created_at: datetime
    updated_at: datetime
```

### Recording
```python
class Recording(Base):
    id: UUID
    call_type_id: UUID           # FK to CallType
    title: str
    client_name: str | None
    recorded_at: datetime | None
    file_path: str               # Path to stored audio/video file
    file_name: str
    duration_seconds: int | None
    status: RecordingStatus      # pending | processing | complete | failed
    scribe_job_id: str | None    # Job ID from Scribe API
    created_at: datetime
    updated_at: datetime
```

### Transcript
```python
class Transcript(Base):
    id: UUID
    recording_id: UUID           # FK to Recording (one-to-one)
    content: str                 # Full raw transcript text
    word_count: int | None
    created_at: datetime
```

### Extraction
```python
class Extraction(Base):
    id: UUID
    recording_id: UUID           # FK to Recording
    prompt_used: str             # Snapshot of prompt at time of extraction
    result: dict                 # JSONB — structured extraction output
    call_type_id: UUID | None    # FK to CallType (for reference)
    created_at: datetime
```

### Query
```python
class Query(Base):
    id: UUID
    recording_id: UUID           # FK to Recording
    question: str                # Ad-hoc question asked by user
    answer: str                  # LLM answer
    created_at: datetime
```

### Enums
```python
class RecordingStatus(str, Enum):
    pending = "pending"
    processing = "processing"
    complete = "complete"
    failed = "failed"
```

---

## API Routes (Backend)

### Call Types
```
GET    /api/call-types           # List all active call types
POST   /api/call-types           # Create new call type
GET    /api/call-types/{id}      # Get single call type
PUT    /api/call-types/{id}      # Update (name, description, prompt_template)
DELETE /api/call-types/{id}      # Soft delete (set is_active=False)
```

### Recordings
```
GET    /api/recordings                  # List recordings (filter by status, call_type)
POST   /api/recordings/upload           # Upload file + metadata, dispatch to Scribe API
GET    /api/recordings/{id}             # Get recording with transcript + extraction
DELETE /api/recordings/{id}             # Delete recording and associated data
POST   /api/recordings/{id}/reprocess   # Re-send to Scribe API
```

### Queries
```
POST   /api/recordings/{id}/queries     # Ask ad-hoc question against transcript
GET    /api/recordings/{id}/queries     # List all queries for a recording
```

---

## Scribe API Integration

The `scribe_client.py` module wraps all communication with the Scribe API.

**Dispatch flow:**
1. User uploads file — Coach App saves file locally — creates Recording (status: pending)
2. Coach App looks up the CallType's `prompt_template`
3. Coach App POSTs file + prompt to Scribe API POST /process
4. Scribe API returns `job_id` — stored on Recording as `scribe_job_id`, status set to processing
5. Background polling task calls GET /job/{id} every 60 seconds
6. On completion — save Transcript and Extraction — Recording status set to complete

**Ad-hoc query flow:**
1. User submits a question on the recording detail page
2. Coach App sends POST /extract to Scribe API with transcript + question as prompt
3. Polls for result — saves Query record — returns answer to UI

**Config:**
```
SCRIBE_API_URL=http://scribe-api:8000
SCRIBE_POLL_INTERVAL_SECONDS=60
```

---

## Seed Data — Default Call Types

Create these on first run via an Alembic seed or startup event:

1. **Quick 15 Min Call**
   Prompt: "Extract the following from this short call transcript: main topic discussed,
   any actions agreed, any follow-up required, and key concerns raised by the client.
   Return as structured JSON."

2. **90-Min Audit Call**
   Prompt: "This is a business audit call. Extract: the business overview provided,
   key challenges identified, current tools and processes mentioned, opportunities
   discussed, recommended actions, and any commitments made. Return as structured JSON."

3. **Coaching Client Call**
   Prompt: "This is a coaching session. Extract: the client's stated goals for this session,
   key insights or breakthroughs, action items agreed, homework or tasks set, and progress
   noted against previous goals. Return as structured JSON."

4. **Full Day Workshop**
   Prompt: "This is a full day workshop recording. Extract: the workshop objectives,
   key topics covered in each session, participant questions or discussion themes,
   decisions made, action items with owners if mentioned, and overall outcomes.
   Return as structured JSON."

---

## Frontend Pages

### Dashboard (/)
- Recent recordings with status indicators
- Quick upload button
- Summary stats (total recordings, processing count)

### Recordings List (/recordings)
- Filterable by call type and status
- Shows client name, call type, date, status
- Link to detail page

### Upload (/recordings/upload)
- File picker (audio/video)
- Call type selector (dropdown from API)
- Client name, title, recorded date fields
- Submit shows processing state

### Recording Detail (/recordings/[id])
- Metadata header (call type, client, date, duration)
- Status badge with polling if still processing
- Transcript tab — full scrollable transcript text
- Extraction tab — renders the structured JSON result in a readable format
- Queries tab — text input to ask follow-up questions, list of previous Q&As

### Call Type Settings (/settings/call-types)
- List of all call types with name and truncated prompt preview
- Edit button — inline form or modal to edit name, description, and prompt template
- Create new call type button
- Toggle active/inactive

---

## Preferred Libraries & Tools

### Backend
- **Core:** FastAPI, Pydantic v2, pydantic-settings, pydantic-ai, SQLAlchemy 2.x, Alembic, httpx
- **Dev tools:** ruff (linter/formatter), pytest — install as dev dependencies via `uv add --dev`
- **Do not** suggest or use pip install, python -m venv, or legacy requirements files

### Frontend
- Nuxt 3, Vue Composition API, Pinia, Tailwind CSS, TypeScript

---

## Environment Variables

### Backend
```
DATABASE_URL=postgresql+asyncpg://coach:coach@postgres:5432/coach
SCRIBE_API_URL=http://scribe-api:8000
SCRIBE_POLL_INTERVAL_SECONDS=60
FILE_STORAGE_PATH=/data/recordings
MAX_UPLOAD_SIZE_MB=1000
API_KEY=changeme
```

### Frontend
```
NUXT_PUBLIC_API_BASE=http://localhost:8001
```

---

## Conventions
- Use `pydantic-settings` for all backend config — no raw `os.environ` calls
- All IDs are UUIDs
- All timestamps are UTC, stored as TIMESTAMP WITH TIME ZONE
- Alembic for all schema migrations — never edit tables manually
- `prompt_used` on Extraction is always a snapshot — changing a CallType prompt
  must not alter historical extractions
- File uploads stored at FILE_STORAGE_PATH/{recording_id}/{original_filename}
- Never delete files immediately — soft-delete the Recording first, then clean up
  files in a scheduled task (future improvement)
- Always include type hints on all backend functions and methods
- Always include tests (pytest) for new backend features — run via `uv run pytest`
- All Python execution must happen via `uv run` to ensure the correct locked environment
