from fastapi import FastAPI
from finance_ai.core.config import settings
from finance_ai.db.session import init_db

app = FastAPI(
    title="Finance AI",
    version="0.1.0",
    description="AI-powered personal finance backend (FastAPI + SQLModel)",
)

@app.on_event("startup")
def on_startup():
    init_db()

@app.get("/", tags=["health"])
def health():
    return {"status": "ok", "env": settings.ENV}