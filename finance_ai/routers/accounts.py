# finance_ai/routers/accounts.py
from __future__ import annotations

from decimal import Decimal
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlmodel import Session, select

from finance_ai.db.models import Account, User
from finance_ai.db.session import get_session
from finance_ai.routers.auth import get_current_user

router = APIRouter(prefix="/api/accounts", tags=["accounts"])


class AccountCreate(BaseModel):
    name: str
    institution: Optional[str] = None
    starting_balance: Decimal = Decimal("0.00")


class AccountRead(BaseModel):
    id: int
    name: str
    institution: Optional[str] = None
    balance: Decimal

    @staticmethod
    def from_model(a: Account) -> "AccountRead":
        return AccountRead(
            id=a.id,
            name=a.name,
            institution=a.institution,
            balance=a.balance,
        )


@router.get("", response_model=List[AccountRead])
def list_accounts(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    rows = session.exec(select(Account).where(Account.user_id == current_user.id)).all()
    return [AccountRead.from_model(a) for a in rows]


@router.post("", response_model=AccountRead, status_code=status.HTTP_201_CREATED)
def create_account(
    payload: AccountCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    acct = Account(
        name=payload.name,
        institution=payload.institution,
        balance=payload.starting_balance,
        user_id=current_user.id,
    )
    session.add(acct)
    session.commit()
    session.refresh(acct)
    return AccountRead.from_model(acct)


@router.get("/{account_id}", response_model=AccountRead)
def get_account(
    account_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    acct = session.get(Account, account_id)
    if not acct or acct.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Account not found")
    return AccountRead.from_model(acct)


@router.delete("/{account_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_account(
    account_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    acct = session.get(Account, account_id)
    if not acct or acct.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Account not found")
    session.delete(acct)
    session.commit()