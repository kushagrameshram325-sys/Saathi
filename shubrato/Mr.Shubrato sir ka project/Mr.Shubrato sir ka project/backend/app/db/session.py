"""
SAATHI database session and engine configuration.

SQLAlchemy setup:
* SQLite is used in development (via DATABASE_URL setting).
* `check_same_thread=False` is required for SQLite with FastAPI's threading model.
* `future=True` enables SQLAlchemy 2.0 execution style.
* `get_db()` is a FastAPI dependency that yields a session and closes it afterward.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.core.config import settings

# Build connection args: SQLite requires check_same_thread=False for multi-threaded use.
_connect_args = (
    {"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}
)

engine = create_engine(
    settings.database_url,
    connect_args=_connect_args,
    future=True,
)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    future=True,
)


class Base(DeclarativeBase):
    """Shared SQLAlchemy declarative base for all ORM models."""
    pass


def get_db():
    """
    FastAPI dependency: yields a database session and ensures it is closed after the request.

    Usage::

        @router.get("/example")
        def example(db: Session = Depends(get_db)):
            ...
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
