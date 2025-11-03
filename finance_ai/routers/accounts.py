# finance_ai/routers/accounts.py
from __future__ import annotations

from decimal import Decimal
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlmodel import Session, select

from finance_ai.db.models import Account, User
from finance_ai.db.session import get_session
from finance_ai.routers.auth import get_current_user

router = APIRouter(prefix="/api/accounts", tags=["accounts"])


class AccountReadResponse(BaseModel):
    id: int
    name: str
    balance: Decimal

    @staticmethod
    def from_model(a: Account) -> "AccountReadResponse":
        return AccountReadResponse(id=a.id, name=a.name, balance=a.balance)


@router.get("", response_model=List[AccountReadResponse])
def list_accounts(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    rows = session.exec(select(Account).where(Account.user_id == current_user.id)).all()
    return [AccountReadResponse.from_model(a) for a in rows]


@router.get("/{account_id}", response_model=AccountReadResponse)
def get_account(
    account_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    acct = session.get(Account, account_id)
    if not acct or acct.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Account not found")
    return AccountReadResponse.from_model(acct)


@router.delete("/{account_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_account(
    account_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    acct = session.get(Account, account_id)
    if not acct or acct.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Account not found")
    session.delete(acct)
    session.commit()