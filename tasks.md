# Yarn Loop Clone — Implementation Tasks

## Phase 0: Project Scaffolding

### T-001: Initialize repository structure
**Files:**
- `backend/` — FastAPI app
- `frontend/` — React/Vite app
- `docker-compose.yml`
- `docker-compose.prod.yml`
- `.env.example`

**Commands:**
```bash
# Backend
uv init backend && cd backend
uv add fastapi uvicorn[standard] sqlalchemy[asyncio] asyncpg alembic \
        pydantic-settings python-jose[cryptography] passlib[bcrypt] \
        python-multipart python-magic boto3 redis

# Frontend
npm create vite@latest frontend -- --template react-ts
cd frontend && npm install @tanstack/react-query @tanstack/react-router \
        zustand tailwindcss @tailwindcss/vite lucide-react
npx shadcn@latest init
```

---

## Phase 1: Database & Migrations

### T-002: Write Alembic initial migration
**File:** `backend/alembic/versions/0001_initial.py`

Apply full schema from spec.md:
- `users`, `projects`, `row_counters`, `stash_items`, `patterns`
- All indexes including GIN on `search_vec` and `patterns.tags`
- Enable `pgcrypto` extension for `gen_random_uuid()`

### T-003: SQLAlchemy async models
**File:** `backend/models.py`

```python
# Signatures required:
class User(Base): ...
class Project(Base): ...
class RowCounter(Base): ...
class StashItem(Base): ...
class Pattern(Base): ...
```

All monetary/measurement columns use `Numeric` (never `Float`).

### T-004: Database session factory
**File:** `backend/database.py`

```python
async def get_db() -> AsyncGenerator[AsyncSession, None]: ...
async def init_db() -> None: ...  # called on startup
```

Use `create_async_engine` with `pool_size=10`, `max_overflow=20`.

---

## Phase 2: Authentication

### T-005: Auth schemas (Pydantic)
**File:** `backend/schemas/auth.py`

```python
class RegisterRequest(BaseModel):
    email: EmailStr
    password: str  # min 8 chars, validated in validator

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
```

### T-006: Auth service
**File:** `backend/services/auth.py`

```python
def hash_password(plain: str) -> str: ...        # bcrypt cost=12
def verify_password(plain: str, hashed: str) -> bool: ...
def create_access_token(user_id: UUID) -> str:   # 15-min JWT
def create_refresh_token(user_id: UUID) -> str:  # 30-day JWT
async def get_current_user(token: str, db: AsyncSession) -> User: ...
```

### T-007: Auth router
**File:** `backend/routers/auth.py`

Endpoints: `POST /auth/register`, `/auth/login`, `/auth/refresh`, `/auth/logout`

Refresh token stored as `HttpOnly; Secure; SameSite=Strict` cookie.
Rate limit login: 5 attempts / 15 min (use `slowapi` with Redis backend).

---

## Phase 3: Projects & Counters

### T-008: Project schemas
**File:** `backend/schemas/projects.py`

```python
class ProjectCreate(BaseModel):
    title: str
    notes: str | None = None
    pattern_id: UUID | None = None
    started_at: date | None = None

class ProjectUpdate(BaseModel):
    title: str | None = None
    status: Literal["active", "frogged", "finished"] | None = None
    notes: str | None = None
    pattern_id: UUID | None = None
    finished_at: date | None = None

class ProjectResponse(BaseModel):
    id: UUID
    title: str
    status: str
    notes: str | None
    counters: list[CounterResponse]
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)
```

### T-009: Projects router
**File:** `backend/routers/projects.py`

ALL queries MUST include `WHERE projects.user_id = current_user.id` — IDOR prevention.

```python
async def list_projects(status: str | None, db, user) -> list[ProjectResponse]: ...
async def create_project(body: ProjectCreate, db, user) -> ProjectResponse: ...
async def get_project(project_id: UUID, db, user) -> ProjectResponse: ...
async def update_project(project_id: UUID, body: ProjectUpdate, db, user) -> ProjectResponse: ...
async def delete_project(project_id: UUID, db, user) -> None: ...
```

### T-010: Row counters router — atomic increments
**File:** `backend/routers/counters.py`

```python
async def increment(counter_id: UUID, db, user) -> CounterResponse:
    # Use UPDATE ... SET current_value = current_value + 1 RETURNING *
    # Subquery ensures ownership: counter.project.user_id == user.id
    # NO Redis. NO fetch-then-save.

async def decrement(counter_id: UUID, db, user) -> CounterResponse:
    # UPDATE ... SET current_value = GREATEST(current_value - 1, 0) RETURNING *

async def reset(counter_id: UUID, db, user) -> CounterResponse:
    # UPDATE ... SET current_value = 0 RETURNING *
```

---

## Phase 4: Stash Management

### T-011: Stash schemas
**File:** `backend/schemas/stash.py`

```python
class StashItemCreate(BaseModel):
    item_type: Literal["yarn", "notion"]
    name: str
    brand: str | None = None
    colorway: str | None = None
    weight_class: Literal["lace","fingering","sport","DK","worsted","aran","bulky","super_bulky"] | None = None
    fiber: str | None = None
    weight_grams: Decimal | None = None   # Decimal, not float
    yardage: Decimal | None = None        # Decimal, not float
    quantity: Decimal = Decimal("1")
    notes: str | None = None
```

### T-012: Stash router
**File:** `backend/routers/stash.py`

```python
async def list_stash(q: str | None, item_type: str | None, db, user) -> list[StashResponse]:
    # Full-text search via: WHERE search_vec @@ plainto_tsquery('english', q)
    # Always filter by user_id

async def create_stash_item(body: StashItemCreate, db, user) -> StashResponse: ...
async def update_stash_item(item_id: UUID, body: StashItemUpdate, db, user) -> StashResponse: ...
async def delete_stash_item(item_id: UUID, db, user) -> None: ...
```

---

## Phase 5: Patterns & File Upload

### T-013: Pattern schemas
**File:** `backend/schemas/patterns.py`

```python
class PatternCreate(BaseModel):
    title: str
    source_url: HttpUrl | None = None
    tags: list[str] = []
    notes: str | None = None

class PatternResponse(BaseModel):
    id: UUID
    title: str
    source_url: str | None
    tags: list[str]
    has_pdf: bool        # True if pdf_key is set
    notes: str | None
    created_at: datetime
```

### T-014: Storage service
**File:** `backend/services/storage.py`

```python
async def upload_file(key: str, content: bytes, content_type: str) -> str: ...
async def generate_presigned_url(key: str, expiry_seconds: int = 3600) -> str: ...
async def delete_file(key: str) -> None: ...
```

Use `aioboto3`. Configure endpoint from `settings.S3_ENDPOINT_URL`.

### T-015: Pattern router with upload
**File:** `backend/routers/patterns.py`

```python
async def upload_pdf(pattern_id: UUID, file: UploadFile, db, user) -> dict:
    content = await file.read()
    # MUST validate with python-magic on raw bytes:
    mime = magic.from_buffer(content[:2048], mime=True)
    if mime != "application/pdf":
        raise HTTPException(400, "File must be a PDF")
    if len(content) > 50 * 1024 * 1024:
        raise HTTPException(413, "Max 50MB")
    key = f"patterns/{user.id}/{pattern_id}.pdf"
    await storage.upload_file(key, content, "application/pdf")
    # Update pattern.pdf_key in DB

async def get_pdf_url(pattern_id: UUID, db, user) -> dict:
    # Returns {"url": presigned_url, "expires_in": 3600}
    # URL is 1-hour TTL pre-signed — never public
```

---

## Phase 6: Frontend Core

### T-016: API client setup
**File:** `frontend/src/lib/api.ts`

Axios instance with:
- `baseURL` from `VITE_API_URL`
- Request interceptor: attach `Authorization: Bearer <access_token>` from memory (not localStorage)
- Response interceptor: on 401, call `/auth/refresh`, retry original request once

### T-017: Auth store + routes
**Files:**
- `frontend/src/stores/authStore.ts` — Zustand store: `{ user, accessToken, login, logout, refresh }`
- `frontend/src/routes/_layout.tsx` — Protected route wrapper
- `frontend/src/routes/login.tsx`
- `frontend/src/routes/register.tsx`

### T-018: Project list page
**File:** `frontend/src/routes/projects/index.tsx`

TanStack Query: `useQuery({ queryKey: ['projects', statusFilter], queryFn: api.getProjects })`

Components: `<ProjectCard>`, `<StatusFilter>`, `<NewProjectSheet>` (shadcn Sheet)

### T-019: Row counter component — optimistic UI
**File:** `frontend/src/components/RowCounter.tsx`

```typescript
// Optimistic update contract:
// 1. tap → store.increment(counterId) immediately (Zustand)
// 2. mutation.mutate() — debounced 150ms
// 3. onSuccess: invalidate query (sync with server truth)
// 4. onError: store.setCount(counterId, previousValue) + toast error
// 5. offline detection: show amber badge if navigator.onLine === false
```

Large tap targets: min 64×64px buttons. Use `onPointerDown` not `onClick`.

### T-020: Stash list with search
**File:** `frontend/src/routes/stash/index.tsx`

Debounced search input (300ms) → `useQuery(['stash', query])` → server-side FTS.
Separate tabs/filters for Yarn vs Notions.

### T-021: Pattern library
**File:** `frontend/src/routes/patterns/index.tsx`

PDF upload with progress indicator. "View PDF" opens pre-signed URL in new tab (no in-browser renderer in v1).

### T-022: Bottom navigation (mobile)
**File:** `frontend/src/components/BottomNav.tsx`

4 items: Projects / Stash / Patterns / Profile.
`min-h-[56px]`, `safe-area-inset-bottom` padding for iOS notch.

---

## Phase 7: Infrastructure

### T-023: Docker Compose (dev)
**File:** `docker-compose.yml`

Services: `api`, `frontend`, `db` (postgres:16), `redis` (redis:7), `minio`.
Hot reload: mount `backend/` as volume into `api` container.

### T-024: Docker Compose (prod)
**File:** `docker-compose.prod.yml`

Services: `api`, `web` (nginx serving Vite build + reverse proxy), `db`, `redis`.
No MinIO — use S3/R2 in prod via env vars.

### T-025: Nginx config
**File:** `nginx/nginx.conf`

```nginx
client_max_body_size 50m;
# Serve /assets/* from Vite build
# Proxy /api/* → api:8000
# HSTS: Strict-Transport-Security: max-age=31536000
```

### T-026: GitHub Actions CI
**File:** `.github/workflows/ci.yml`

Steps: ruff lint, mypy, pytest, eslint, tsc, `npm audit --audit-level=high`, Docker build validation.
Add `pip-audit` gate: fail CI on any HIGH/CRITICAL CVE.

### T-027: GitHub Actions Deploy
**File:** `.github/workflows/deploy.yml`

Trigger: push to `main`.
Steps: build images → push GHCR → SSH to VPS → `docker compose pull && docker compose up -d`.

---

## Phase 8: Observability & Backup

### T-028: Sentry integration
**Files:**
- `backend/main.py` — `sentry_sdk.init(dsn=settings.SENTRY_DSN)`
- `frontend/src/main.tsx` — `Sentry.init(...)` with React error boundary

### T-029: Database backup cron
**File:** `scripts/backup.sh`

Daily `pg_dump` → compress → upload to Backblaze B2 via `rclone`.
Register as systemd timer or Docker cron container.

### T-030: Environment template
**File:** `.env.example`

```
DATABASE_URL=postgresql+asyncpg://yarn:yarn@db:5432/yarn
REDIS_URL=redis://redis:6379/0
SECRET_KEY=change-me-in-prod
S3_ENDPOINT_URL=http://minio:9000
S3_BUCKET=yarn-loop
S3_ACCESS_KEY=minioadmin
S3_SECRET_KEY=minioadmin
SENTRY_DSN=
```

---

## Task Summary

| Phase | Tasks | Key Risk | Status |
|-------|-------|----------|--------|
| 0: Scaffolding | T-001 | Vite + FastAPI CORS config | [x] |
| 1: Database | T-002–T-004 | GIN index on TSVECTOR | [x] |
| 2: Auth | T-005–T-007 | Refresh token rotation | [x] |
| 3: Projects/Counters | T-008–T-010 | IDOR, atomic SQL increments | [ ] |
| 4: Stash | T-011–T-012 | FTS query performance | [ ] |
| 5: Patterns/Upload | T-013–T-015 | python-magic MIME validation | [ ] |
| 6: Frontend | T-016–T-022 | Optimistic counter rollback | [ ] |
| 7: Infrastructure | T-023–T-027 | Secrets management | [ ] |
| 8: Ops | T-028–T-030 | Backup reliability | [ ] |
