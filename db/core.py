import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

Base = declarative_base()


def normalize_database_url(url: str) -> str:
    """Ensure SQLAlchemy URL uses psycopg driver for Postgres.

    - Accepts postgresql:// and postgres:// and converts to postgresql+psycopg://
    - Leaves other schemes intact
    """
    if url.startswith("postgres://"):
        return url.replace("postgres://", "postgresql+psycopg://", 1)
    if url.startswith("postgresql://") and "+" not in url.split("://", 1)[0]:
        return url.replace("postgresql://", "postgresql+psycopg://", 1)
    return url


def build_engine_from_env() -> tuple | None:
    """Build a SQLAlchemy engine + sessionmaker from env DATABASE_URL.

    Returns (engine, SessionLocal) or None if DATABASE_URL is not set.
    """
    url = os.getenv("DATABASE_URL")
    if not url:
        return None
    url = normalize_database_url(url)
    engine = create_engine(url, pool_pre_ping=True)
    SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)
    return engine, SessionLocal

