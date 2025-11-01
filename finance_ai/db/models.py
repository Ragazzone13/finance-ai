from __future__ import annotations

from datetime import date, datetime
from typing import Optional

from sqlmodel import Field, SQLModel


class Timestamped(SQLModel):
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)


class User(Timestamped, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(index=True, unique=True)
    password_hash: str


class Account(Timestamped, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(index=True)
    name: str
    acct_type: str = Field(default="checking", index=True)


class Category(Timestamped, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(index=True)
    name: str = Field(index=True)
    parent_id: Optional[int] = Field(default=None, index=True)


class Transaction(Timestamped, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(index=True)
    account_id: Optional[int] = Field(default=None, index=True)
    date: date = Field(index=True)
    amount: float
    txn_type: str = Field(index=True)  # debit | credit
    category_id: Optional[int] = Field(default=None, index=True)
    vendor: Optional[str] = Field(default=None, index=True)
    note: Optional[str] = None
    is_recurring: bool = Field(default=False)
    source: str = Field(default="manual", index=True)
    hash_key: Optional[str] = Field(default=None, index=True)


class Budget(Timestamped, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(index=True)
    month: str = Field(index=True)  # "YYYY-MM"
    category_id: int = Field(index=True)
    amount: float


class Goal(Timestamped, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(index=True)
    name: str
    target_amount: float
    target_date: Optional[date] = None


class Insight(Timestamped, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(index=True)
    insight_type: str = Field(index=True)
    payload: str
    resolved: bool = Field(default=False)