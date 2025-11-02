from __future__ import annotations

from sqlmodel import SQLModel, create_engine, Session
from finance_ai.core.config import settings

# For SQLite dev: create tables automatically. For Postgres in prod: use Alembic.
engine = create_engine(settings.DATABASE_URL, echo=False)


def init_db() -> None:
    if settings.DATABASE_URL.startswith("sqlite"):
        SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session