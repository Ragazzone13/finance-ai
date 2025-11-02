# finance_ai/routers/health.py
from __future__ import annotations

from fastapi import APIRouter
from sqlalchemy import text
from sqlmodel import Session, select

from finance_ai.db.session import engine
from finance_ai.db.models import User

router = APIRouter(tags=["meta"])


@router.get("/healthz")
def healthz():
    return {"status": "ok"}


@router.get("/health/db")
def health_db():
    try:
        # Basic DB ping
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))

        # Ensure we can query a table mapped by SQLModel
        with Session(engine) as session:
            session.exec(select(User).limit(1)).all()

        return {"status": "ok", "db": "connected"}
    except Exception as e:
        return {"status": "degraded", "db": f"error: {type(e).__name__}: {e}"}