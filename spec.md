# Yarn Loop Clone — Product Specification

## Executive Summary

Yarn Loop Clone is a mobile-first social crafting app for knitters and crocheters. Users log projects, track yarn inventory, follow patterns, and share progress with a community feed. The app operates offline-first with background sync, targeting iOS and Android via a single React Native codebase.

---

## Tech Stack

| Layer | Technology | Rationale |
|---|---|---|
| Mobile | React Native (Expo) | Single codebase, strong community, OTA updates |
| Local DB | WatermelonDB | Lazy-loading, offline-first, SQLite-backed |
| API | FastAPI (Python) | Async I/O, auto OpenAPI docs, Pydantic validation |
| Database | PostgreSQL 16 | JSONB for flexible pattern metadata, strong relational integrity |
| Auth | Supabase Auth (JWT) | Managed auth, RLS policies, social login support |
| Storage | S3-compatible (Supabase Storage) | Project photos, pattern PDFs |
| Cache | Redis | Feed fanout cache, rate limiting |

---

## Architecture Overview

```
┌─────────────────────────────────────────┐
│           React Native (Expo)           │
│  ┌────────────┐   ┌──────────────────┐  │
│  │WatermelonDB│◄──│  Sync Engine     │  │
│  │(SQLite)    │   │(delta pull/push) │  │
│  └────────────┘   └────────┬─────────┘  │
└───────────────────────────┼─────────────┘
                            │ HTTPS/REST
                 ┌──────────▼──────────┐
                 │   FastAPI Backend   │
                 │  ┌───────────────┐  │
                 │  │ Auth Middleware│  │
                 │  │ (JWT / Supabase│  │
                 │  └───────────────┘  │
                 └──┬──────────┬───────┘
                    │          │
             ┌──────▼───┐  ┌───▼──────┐
             │PostgreSQL│  │  Redis   │
             │          │  │  Cache   │
             └──────────┘  └──────────┘
```

**Sync Pattern:** Pull-based delta sync on app foreground. Client sends `last_synced_at`; server returns changed records. Conflicts resolved server-wins with client timestamp logging.

---

## Core Data Models

- **User** — profile, bio, follower graph
- **Project** — name, status (queued/active/finished), yarn refs, pattern ref, photos[]
- **Yarn** — brand, colorway, weight, stash quantity (use `Numeric` for quantities)
- **Pattern** — title, source URL, PDF attachment, tags[]
- **FeedPost** — project_id, caption, likes[], comments[]

---

## Key Architectural Risks

1. **Sync conflicts** — Two devices editing the same project offline. Mitigation: server-wins with per-field timestamps; surface conflicts in UI.
2. **Feed fanout at scale** — Popular users posting triggers many cache invalidations. Mitigation: async fanout via Redis pub/sub, paginated pull model initially.
3. **Offline photo uploads** — Large files queued locally may fail silently. Mitigation: resumable uploads (S3 multipart), local job queue with retry state.
4. **WatermelonDB schema migrations** — Breaking changes require careful versioning. Mitigation: explicit migration scripts, tested on each Expo update.
5. **App store compliance** — User-generated content requires moderation hooks from day one.