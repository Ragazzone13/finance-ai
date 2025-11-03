# finance_ai/db/session.py
from __future__ import annotations

from typing import Generator

from sqlmodel import SQLModel, create_engine, Session
from finance_ai.core.config import settings


def get_database_url() -> str:
    return settings.DATABASE_URL


engine = create_engine(
    get_database_url(),
    echo=bool(getattr(settings, "SQLALCHEMY_ECHO", False)),
    future=True,
)


def init_db() -> None:
    # For SQLite dev: create tables automatically. For Postgres/prod: use Alembic.
    db_url = get_database_url()
    if db_url.startswith("sqlite"):
        SQLModel.metadata.create_all(engine)


def get_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session


def get_alembic_url() -> str:
    # Alembic env.py will call this if DATABASE_URL is not set in the shell
    return get_database_url()