# Yarn Loop Clone — Implementation Tasks

## Phase 0: Project Scaffolding

### T-001: Initialize repository structure [x]
**Files:**
- `backend/` — FastAPI app
- `frontend/` — React/Vite app
- `docker-compose.yml`
- `docker-compose.prod.yml`
- `.env.example`

---

## Phase 1: Database & Migrations

### T-002: Write Alembic initial migration [x]
### T-003: SQLAlchemy async models [x]
### T-004: Database session factory [x]

---

## Phase 2: Authentication

### T-005: Auth schemas (Pydantic) [x]
### T-006: Auth service [x]
### T-007: Auth router [x]

---

## Phase 3: Projects & Counters

### T-008: Project schemas [x]
### T-009: Projects router [x]
### T-010: Row counters router — atomic increments [x]

---

## Phase 4: Stash Management

### T-011: Stash schemas [x]
### T-012: Stash router [x]

---

## Phase 5: Patterns & File Upload

### T-013: Pattern schemas [x]
### T-014: Storage service [x]
### T-015: Pattern router with upload [x]

---

## Phase 6: Frontend Core

### T-016: API client setup [x]
### T-017: Auth store + routes [x]
### T-018: Project list page [x]
### T-019: Row counter component — optimistic UI [x]
### T-020: Stash list with search [x]
### T-021: Pattern library [x]
### T-022: Bottom navigation (mobile) [x]

---

## Phase 7: Infrastructure

### T-023: Docker Compose (dev) [x]
### T-024: Docker Compose (prod) [x]
### T-025: Nginx config [x]
### T-026: GitHub Actions CI [ ]
### T-027: GitHub Actions Deploy [ ]

---

## Phase 8: Observability & Backup

### T-028: Sentry integration [ ]
### T-029: Database backup cron [ ]
### T-030: Environment template [x]

---

## Task Summary

| Phase | Status |
|-------|--------|
| 0: Scaffolding | [x] |
| 1: Database | [x] |
| 2: Auth | [x] |
| 3: Projects/Counters | [x] |
| 4: Stash | [x] |
| 5: Patterns/Upload | [x] |
| 6: Frontend | [x] |
| 7: Infrastructure | [x] |
| 8: Ops | [ ] |
