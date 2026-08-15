"""Database engine + session factory (SQLite dev / PostgreSQL prod, with a
serverless-friendly fallback to /tmp for Vercel)."""

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import get_settings

settings = get_settings()

DB_URL = settings.DATABASE_URL

# On Vercel serverless, the filesystem is read-only except /tmp — keep SQLite there.
if settings.is_vercel and DB_URL.startswith("sqlite:///"):
    DB_URL = "sqlite:////tmp/waqt.db"

connect_args = {"check_same_thread": False} if DB_URL.startswith("sqlite") else {}

if DB_URL == "sqlite:///:memory:":
    # Shared single connection so all sessions see the same in-memory DB (tests).
    from sqlalchemy.pool import StaticPool

    engine = create_engine(
        DB_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        pool_pre_ping=True,
    )
else:
    engine = create_engine(DB_URL, connect_args=connect_args, pool_pre_ping=True)

SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


def get_db():
    """FastAPI dependency that yields a scoped session."""
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """Create all tables (import models so they register on Base.metadata)."""
    from app.models import Base  # noqa: F401

    Base.metadata.create_all(bind=engine)
