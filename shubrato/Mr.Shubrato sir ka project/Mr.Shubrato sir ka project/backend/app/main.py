"""
SAATHI FastAPI application entry point.

Responsibilities
----------------
* Create and configure the FastAPI application.
* Register CORS middleware (restricted origins per settings).
* Mount the API router at the configured prefix.
* Provide a root status endpoint.
* On startup: create all database tables and seed the support-service directory
  with demo listings if the table is empty.
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import router
from app.api.auth import auth_router
from app.core.config import settings
from app.db.session import Base, SessionLocal, engine
from app.models import entities  # noqa: F401  – registers all ORM models with Base
from app.services.seed import seed_services

logger = logging.getLogger("saathi")


# ---------------------------------------------------------------------------
# Startup / shutdown lifecycle
# ---------------------------------------------------------------------------

@asynccontextmanager
async def lifespan(app: FastAPI):  # type: ignore[type-arg]
    """
    Application lifespan handler.

    * Creates all SQLAlchemy tables (no-op if they already exist).
    * Seeds the support-service directory with demo listings when empty.
    """
    logger.info("SAATHI API starting – creating database tables …")
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        seed_services(db)
        logger.info("Database seeding complete.")
    finally:
        db.close()

    yield  # application is running

    logger.info("SAATHI API shutting down.")


# ---------------------------------------------------------------------------
# Application
# ---------------------------------------------------------------------------

app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    description=(
        "SAATHI – Trusted Safety Support Network API.\n\n"
        "Provides a support-service directory, community hazard reporting, "
        "and a private support-preference workflow.\n\n"
        "**Privacy note**: this is a development prototype. "
        "Do not store real survivor data until a full privacy and security review "
        "has been completed and production safeguards are in place."
    ),
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Allow the frontend dev server and any configured origins to call the API.
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

# Mount all API routes under /api/v1 (configurable via settings).
app.include_router(router, prefix=settings.api_prefix)
app.include_router(auth_router, prefix=settings.api_prefix)


# ---------------------------------------------------------------------------
# Root
# ---------------------------------------------------------------------------

@app.get("/", summary="Root status", tags=["Meta"])
def root():
    """Quick reachability check; returns pointers to the health and docs endpoints."""
    return {
        "name": "SAATHI API",
        "status": "running",
        "docs": "/docs",
        "redoc": "/redoc",
        "health": f"{settings.api_prefix}/health",
    }
