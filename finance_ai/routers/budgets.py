# finance_ai/routers/budgets.py
from __future__ import annotations

from decimal import Decimal
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlmodel import Session, select

from finance_ai.db.models import Budget, User
from finance_ai.db.session import get_session
from finance_ai.routers.auth import get_current_user

router = APIRouter(prefix="/api/budgets", tags=["budgets"])


class BudgetCreate(BaseModel):
    category_id: int
    month: str  # "YYYY-MM"
    amount: Decimal


class BudgetRead(BaseModel):
    id: int
    category_id: int
    month: str
    amount: Decimal

    @staticmethod
    def from_model(b: Budget) -> "BudgetRead":
        return BudgetRead(id=b.id, category_id=b.category_id, month=b.month, amount=b.amount)


@router.get("", response_model=List[BudgetRead])
def list_budgets(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
    month: Optional[str] = None,
):
    query = select(Budget).where(Budget.user_id == current_user.id)
    if month:
        query = query.where(Budget.month == month)
    rows = session.exec(query.order_by(Budget.month.desc(), Budget.id.desc())).all()
    return [BudgetRead.from_model(b) for b in rows]


@router.post("", response_model=BudgetRead, status_code=status.HTTP_201_CREATED)
def create_budget(
    payload: BudgetCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    # prevent duplicates for same user/category/month
    exists = session.exec(
        select(Budget).where(
            Budget.user_id == current_user.id,
            Budget.category_id == payload.category_id,
            Budget.month == payload.month,
        )
    ).first()
    if exists:
        raise HTTPException(status_code=409, detail="Budget already exists for that category/month")

    b = Budget(
        user_id=current_user.id,
        category_id=payload.category_id,
        month=payload.month,
        amount=payload.amount,
    )
    session.add(b)
    session.commit()
    session.refresh(b)
    return BudgetRead.from_model(b)