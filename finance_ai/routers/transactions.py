# finance_ai/routers/transactions.py
from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlmodel import Session, select

from finance_ai.db.models import Account, Transaction, User
from finance_ai.db.session import get_session
from finance_ai.routers.auth import get_current_user

router = APIRouter(prefix="/api/transactions", tags=["transactions"])


class TransactionCreate(BaseModel):
    account_id: int
    amount: Decimal
    type: str  # "debit" | "credit"
    occurred_on: date
    description: Optional[str] = None
    category_id: Optional[int] = None


class TransactionRead(BaseModel):
    id: int
    account_id: int
    amount: Decimal
    type: str
    occurred_on: date
    description: Optional[str] = None
    category_id: Optional[int] = None

    @staticmethod
    def from_model(t: Transaction) -> "TransactionRead":
        return TransactionRead(
            id=t.id,
            account_id=t.account_id,
            amount=t.amount,
            type=t.type,
            occurred_on=t.occurred_on,
            description=t.description,
            category_id=t.category_id,
        )


def _ensure_account_owned(session: Session, user_id: int, account_id: int) -> Account:
    acct = session.get(Account, account_id)
    if not acct or acct.user_id != user_id:
        raise HTTPException(status_code=404, detail="Account not found")
    return acct


@router.get("", response_model=List[TransactionRead])
def list_transactions(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
    account_id: Optional[int] = Query(None),
):
    query = select(Transaction).join(Account).where(Account.user_id == current_user.id)
    if account_id:
        _ensure_account_owned(session, current_user.id, account_id)
        query = query.where(Transaction.account_id == account_id)

    rows = session.exec(query.order_by(Transaction.occurred_on.desc(), Transaction.id.desc())).all()
    return [TransactionRead.from_model(t) for t in rows]


@router.post("", response_model=TransactionRead, status_code=status.HTTP_201_CREATED)
def create_transaction(
    payload: TransactionCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    _ensure_account_owned(session, current_user.id, payload.account_id)

    t = Transaction(
        account_id=payload.account_id,
        amount=payload.amount,
        type=payload.type,
        occurred_on=payload.occurred_on,
        description=payload.description,
        category_id=payload.category_id,
    )
    session.add(t)
    session.commit()
    session.refresh(t)
    return TransactionRead.from_model(t)


@router.delete("/{transaction_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_transaction(
    transaction_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    t = session.get(Transaction, transaction_id)
    if not t:
        raise HTTPException(status_code=404, detail="Transaction not found")
    _ensure_account_owned(session, current_user.id, t.account_id)

    session.delete(t)
    session.commit()