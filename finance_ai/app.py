# finance_ai/app.py
from __future__ import annotations
import os
from typing import List

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from finance_ai.routers import health
from finance_ai.routers import auth
from finance_ai.routers import accounts
from finance_ai.routers import categories
from finance_ai.routers import budgets
from finance_ai.routers import transactions
from finance_ai.routers import aggregations
from finance_ai.routers import budget_compare

app = FastAPI(
    title="Finance AI",
    version="0.1.0",
    description="Backend API for the Finance AI app.",
)

app.include_router(health.router)
app.include_router(auth.router)
app.include_router(accounts.router)
app.include_router(categories.router)
app.include_router(budgets.router)
app.include_router(transactions.router)
app.include_router(aggregations.router)
app.include_router(budget_compare.router)

_default_origins: List[str] = [
    "http://localhost",
    "http://localhost:3000",
    "http://127.0.0.1",
    "http://127.0.0.1:3000",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]
_env_origins = os.getenv("CORS_ORIGINS", "")
origins = [o.strip() for o in _env_origins.split(",") if o.strip()] or _default_origins

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/", tags=["meta"])
def read_root():
    return {
        "status": "ok",
        "message": "Finance AI backend is running.",
        "docs": "/docs",
        "redoc": "/redoc",
    }