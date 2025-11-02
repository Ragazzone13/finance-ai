# finance_ai/routers/budget_compare.py
from __future__ import annotations

from decimal import Decimal
from typing import Dict

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlmodel import Session, select

from finance_ai.db.models import Budget, Transaction, User
from finance_ai.db.session import get_session
from finance_ai.routers.auth import get_current_user

router = APIRouter(prefix="/api/budget", tags=["budget-compare"])


class BudgetComparison(BaseModel):
    month: str
    totals: Dict[int, Dict[str, Decimal]]  # {category_id: {budgeted, actual, delta}}


@router.get("/compare", response_model=BudgetComparison)
def compare(
    month: str = Query(..., description="YYYY-MM"),
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    month_like = f"{month}-%"

    budgets = session.exec(
        select(Budget.category_id, Budget.amount).where(Budget.user_id == current_user.id, Budget.month == month)
    ).all()

    actuals = session.exec(
        select(Transaction.category_id, Transaction.type, Transaction.amount)
        .where(Transaction.user_id == current_user.id, Transaction.occurred_on.like(month_like))
    ).all()

    totals: Dict[int, Dict[str, Decimal]] = {}
    for category_id, amount in budgets:
        totals[int(category_id)] = {"budgeted": Decimal(amount), "actual": Decimal("0.00"), "delta": Decimal("0.00")}

    for category_id, tx_type, amount in actuals:
        if category_id is None:
            continue
        if tx_type == "debit":
            totals.setdefault(int(category_id), {"budgeted": Decimal("0.00"), "actual": Decimal("0.00"), "delta": Decimal("0.00")})
            totals[int(category_id)]["actual"] += Decimal(amount)

    for cid, entry in totals.items():
        entry["delta"] = entry["budgeted"] - entry["actual"]

    return BudgetComparison(month=month, totals=totals)