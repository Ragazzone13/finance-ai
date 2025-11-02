# finance_ai/routers/transactions.py
from __future__ import annotations

import datetime as dt
from decimal import Decimal
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, field_validator
from sqlmodel import Session, select

from finance_ai.db.models import Transaction, User
from finance_ai.db.session import get_session
from finance_ai.deps.users import get_current_user

router = APIRouter(prefix="/api/transactions", tags=["transactions"])


class TransactionCreate(BaseModel):
    account_id: Optional[int] = None
    date: dt.date
    amount: Decimal
    txn_type: str  # "debit" | "credit"
    category_id: Optional[int] = None
    vendor: Optional[str] = None
    note: Optional[str] = None
    is_recurring: bool = False
    source: str = "manual"
    hash_key: Optional[str] = None

    @field_validator("txn_type")
    @classmethod
    def validate_txn_type(cls, v: str) -> str:
        v = v.lower().strip()
        if v not in {"debit", "credit"}:
            raise ValueError("txn_type must be 'debit' or 'credit'")
        return v


class TransactionUpdate(BaseModel):
    account_id: Optional[int] = None
    date: Optional[dt.date] = None
    amount: Optional[Decimal] = None
    txn_type: Optional[str] = None
    category_id: Optional[int] = None
    vendor: Optional[str] = None
    note: Optional[str] = None
    is_recurring: Optional[bool] = None
    source: Optional[str] = None
    hash_key: Optional[str] = None

    @field_validator("txn_type")
    @classmethod
    def validate_txn_type(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        v2 = v.lower().strip()
        if v2 not in {"debit", "credit"}:
            raise ValueError("txn_type must be 'debit' or 'credit'")
        return v2


class TransactionRead(BaseModel):
    id: int
    user_id: int
    account_id: Optional[int]
    date: dt.date
    amount: Decimal
    txn_type: str
    category_id: Optional[int]
    vendor: Optional[str]
    note: Optional[str]
    is_recurring: bool
    source: str
    hash_key: Optional[str]

    class Config:
        from_attributes = True


@router.post("", response_model=TransactionRead, status_code=201)
def create_transaction(
    payload: TransactionCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    txn = Transaction(user_id=current_user.id, **payload.model_dump())
    session.add(txn)
    session.commit()
    session.refresh(txn)
    return txn


@router.get("", response_model=List[TransactionRead])
def list_transactions(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
    account_id: Optional[int] = Query(None),
    category_id: Optional[int] = Query(None),
    start_date: Optional[dt.date] = Query(None),
    end_date: Optional[dt.date] = Query(None),
    txn_type: Optional[str] = Query(None),
    vendor: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
):
    stmt = select(Transaction).where(Transaction.user_id == current_user.id)

    if account_id is not None:
        stmt = stmt.where(Transaction.account_id == account_id)
    if category_id is not None:
        stmt = stmt.where(Transaction.category_id == category_id)
    if start_date is not None:
        stmt = stmt.where(Transaction.date >= start_date)
    if end_date is not None:
        stmt = stmt.where(Transaction.date <= end_date)
    if txn_type is not None:
        t = txn_type.lower().strip()
        if t not in {"debit", "credit"}:
            raise HTTPException(status_code=400, detail="txn_type must be 'debit' or 'credit'")
        stmt = stmt.where(Transaction.txn_type == t)
    if vendor is not None:
        stmt = stmt.where(Transaction.vendor == vendor)

    stmt = stmt.order_by(Transaction.date.desc(), Transaction.id.desc()).limit(limit).offset(offset)
    rows = session.exec(stmt).all()
    return rows


@router.get("/{txn_id}", response_model=TransactionRead)
def get_transaction(
    txn_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    txn = session.get(Transaction, txn_id)
    if not txn or txn.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return txn


@router.patch("/{txn_id}", response_model=TransactionRead)
def update_transaction(
    txn_id: int,
    payload: TransactionUpdate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    txn = session.get(Transaction, txn_id)
    if not txn or txn.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Transaction not found")

    data = payload.model_dump(exclude_unset=True)
    if "txn_type" in data and data["txn_type"] is not None:
        data["txn_type"] = data["txn_type"].lower().strip()

    for k, v in data.items():
        setattr(txn, k, v)
    txn.updated_at = dt.datetime.now(dt.timezone.utc)

    session.add(txn)
    session.commit()
    session.refresh(txn)
    return txn


@router.delete("/{txn_id}", status_code=204)
def delete_transaction(
    txn_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    txn = session.get(Transaction, txn_id)
    if not txn or txn.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Transaction not found")
    session.delete(txn)
    session.commit()
    return None