# finance_ai/routers/accounts.py
from __future__ import annotations

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlmodel import Session, select

from finance_ai.db.models import Account, User
from finance_ai.db.session import get_session
from finance_ai.deps.users import get_current_user

router = APIRouter(prefix="/api/accounts", tags=["accounts"])


class AccountCreate(BaseModel):
    name: str
    acct_type: str = "checking"


class AccountUpdate(BaseModel):
    name: Optional[str] = None
    acct_type: Optional[str] = None


class AccountRead(BaseModel):
    id: int
    user_id: int
    name: str
    acct_type: str

    class Config:
        from_attributes = True


@router.post("", response_model=AccountRead, status_code=201)
def create_account(
    payload: AccountCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    acct = Account(user_id=current_user.id, **payload.model_dump())
    session.add(acct)
    session.commit()
    session.refresh(acct)
    return acct


@router.get("", response_model=List[AccountRead])
def list_accounts(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
    name: Optional[str] = Query(None, description="Filter by name (exact match)"),
    acct_type: Optional[str] = Query(None, description="Filter by acct_type"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
):
    stmt = select(Account).where(Account.user_id == current_user.id)
    if name:
        stmt = stmt.where(Account.name == name)
    if acct_type:
        stmt = stmt.where(Account.acct_type == acct_type)
    stmt = stmt.order_by(Account.id.desc()).limit(limit).offset(offset)
    results = session.exec(stmt).all()
    return results


@router.get("/{account_id}", response_model=AccountRead)
def get_account(
    account_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    acct = session.get(Account, account_id)
    if not acct or acct.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Account not found")
    return acct


@router.patch("/{account_id}", response_model=AccountRead)
def update_account(
    account_id: int,
    payload: AccountUpdate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    acct = session.get(Account, account_id)
    if not acct or acct.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Account not found")

    data = payload.model_dump(exclude_unset=True)
    for k, v in data.items():
        setattr(acct, k, v)
    session.add(acct)
    session.commit()
    session.refresh(acct)
    return acct


@router.delete("/{account_id}", status_code=204)
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
    return None