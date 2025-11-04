import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

Base = declarative_base()


def normalize_database_url(url: str) -> str:
    """Normalise l'URL de base de données pour SQLAlchemy (Postgres psycopg).

    - Accepte les schémas ``postgresql://`` et ``postgres://`` et les convertit en
      ``postgresql+psycopg://`` pour le driver moderne.
    - Laisse les autres schémas intacts.
    """
    if url.startswith("postgres://"):
        return url.replace("postgres://", "postgresql+psycopg://", 1)
    if url.startswith("postgresql://") and "+" not in url.split("://", 1)[0]:
        return url.replace("postgresql://", "postgresql+psycopg://", 1)
    return url


def build_engine_from_env() -> tuple | None:
    """Construit un engine SQLAlchemy + sessionmaker à partir de ``DATABASE_URL``.

    Retourne ``(engine, SessionLocal)`` ou ``None`` si la variable n'est pas définie.
    """
    url = os.getenv("DATABASE_URL")
    if not url:
        return None
    url = normalize_database_url(url)
    engine = create_engine(url, pool_pre_ping=True)
    SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)
    return engine, SessionLocal
"""Outils de configuration SQLAlchemy (engine/session) et normalisation d'URL DB."""
