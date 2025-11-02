# finance_ai/routers/budgets.py
from __future__ import annotations

from decimal import Decimal
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, field_validator
from sqlmodel import Session, select

from finance_ai.db.models import Budget, Category, User
from finance_ai.db.session import get_session
from finance_ai.deps.users import get_current_user

router = APIRouter(prefix="/api/budgets", tags=["budgets"])


class BudgetCreate(BaseModel):
    month: str  # "YYYY-MM"
    category_id: int
    amount: Decimal

    @field_validator("month")
    @classmethod
    def valid_month(cls, v: str) -> str:
        v2 = v.strip()
        parts = v2.split("-")
        if len(parts) != 2:
            raise ValueError("month must be 'YYYY-MM'")
        y, m = parts
        if not (y.isdigit() and m.isdigit()):
            raise ValueError("month must be 'YYYY-MM'")
        if int(m) < 1 or int(m) > 12:
            raise ValueError("month must be 'YYYY-MM'")
        return v2


class BudgetUpdate(BaseModel):
    amount: Optional[Decimal] = None


class BudgetRead(BaseModel):
    id: int
    user_id: int
    month: str
    category_id: int
    amount: Decimal

    class Config:
        from_attributes = True


@router.post("", response_model=BudgetRead, status_code=201)
def create_budget(
    payload: BudgetCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    # Validate category ownership
    cat = session.get(Category, payload.category_id)
    if not cat or cat.user_id != current_user.id:
        raise HTTPException(status_code=400, detail="Invalid category_id for user")

    # Enforce unique (user_id, month, category_id)
    existing = session.exec(
        select(Budget).where(
            Budget.user_id == current_user.id,
            Budget.month == payload.month,
            Budget.category_id == payload.category_id,
        )
    ).first()
    if existing:
        raise HTTPException(status_code=409, detail="Budget already exists for month+category")

    row = Budget(user_id=current_user.id, **payload.model_dump())
    session.add(row)
    session.commit()
    session.refresh(row)
    return row


@router.get("", response_model=List[BudgetRead])
def list_budgets(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
    month: Optional[str] = Query(None),
    category_id: Optional[int] = Query(None),
    limit: int = Query(200, ge=1, le=1000),
    offset: int = Query(0, ge=0),
):
    stmt = select(Budget).where(Budget.user_id == current_user.id)
    if month:
        stmt = stmt.where(Budget.month == month)
    if category_id is not None:
        stmt = stmt.where(Budget.category_id == category_id)
    stmt = stmt.order_by(Budget.month.desc(), Budget.id.desc()).limit(limit).offset(offset)
    return session.exec(stmt).all()


@router.get("/{budget_id}", response_model=BudgetRead)
def get_budget(
    budget_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    row = session.get(Budget, budget_id)
    if not row or row.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Budget not found")
    return row


@router.patch("/{budget_id}", response_model=BudgetRead)
def update_budget(
    budget_id: int,
    payload: BudgetUpdate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    row = session.get(Budget, budget_id)
    if not row or row.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Budget not found")
    data = payload.model_dump(exclude_unset=True)
    for k, v in data.items():
        setattr(row, k, v)
    session.add(row)
    session.commit()
    session.refresh(row)
    return row


@router.delete("/{budget_id}", status_code=204)
def delete_budget(
    budget_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    row = session.get(Budget, budget_id)
    if not row or row.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Budget not found")
    session.delete(row)
    session.commit()
    return None