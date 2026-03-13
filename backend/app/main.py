import os
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.starlette import StarletteIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
from sentry_sdk.integrations.logging import LoggingIntegration
import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# ── Sentry (T-028) ────────────────────────────────────────────────────────────
SENTRY_DSN = os.getenv("SENTRY_DSN", "")
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")

if SENTRY_DSN:
    sentry_sdk.init(
        dsn=SENTRY_DSN,
        environment=ENVIRONMENT,
        traces_sample_rate=1.0 if ENVIRONMENT == "development" else 0.2,
        profiles_sample_rate=0.1,
        integrations=[
            StarletteIntegration(transaction_style="endpoint"),
            FastApiIntegration(transaction_style="endpoint"),
            SqlalchemyIntegration(),
            LoggingIntegration(
                level=logging.INFO,        # Breadcrumbs from INFO+
                event_level=logging.ERROR, # Events from ERROR+
            ),
        ],
        send_default_pii=False,  # GDPR-safe: no PII by default
    )

# ── App ───────────────────────────────────────────────────────────────────────
app = FastAPI(
    title="Yarn Loop API",
    version="1.0.0",
    docs_url="/api/docs" if ENVIRONMENT != "production" else None,
    redoc_url=None,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Health ────────────────────────────────────────────────────────────────────
@app.get("/health", tags=["infra"])
async def health_check():
    return {"status": "ok", "environment": ENVIRONMENT}

# ── Sentry debug route (remove in prod) ──────────────────────────────────────
@app.get("/sentry-debug", include_in_schema=False)
async def trigger_error():
    """Intentional divide-by-zero to verify Sentry pipeline."""
    _ = 1 / 0

# ── Routers ───────────────────────────────────────────────────────────────────
from app.routers import auth, projects, counters, patterns, stash

app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(projects.router, prefix="/api/v1/projects", tags=["projects"])
app.include_router(counters.router, prefix="/api/v1/counters", tags=["counters"])
app.include_router(patterns.router, prefix="/api/v1/patterns", tags=["patterns"])
app.include_router(stash.router, prefix="/api/v1/stash", tags=["stash"])
