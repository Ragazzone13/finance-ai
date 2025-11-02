# finance_ai/routers/budget_compare.py
from __future__ import annotations

import datetime as dt
from decimal import Decimal
from typing import Dict, List, Optional, Tuple

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import func
from sqlmodel import Session, select

from finance_ai.db.models import Budget, Category, Transaction, User
from finance_ai.db.session import get_session
from finance_ai.deps.users import get_current_user

router = APIRouter(prefix="/api/budget", tags=["budget"])


class CategoryBudgetActual(BaseModel):
    category_id: int
    category_name: Optional[str]
    budgeted: Decimal
    actual: Decimal
    variance: Decimal  # budgeted - actual (positive means under budget)


class BudgetMonthReport(BaseModel):
    month: str
    user_id: int
    account_id: Optional[int]
    totals: List[CategoryBudgetActual]
    budget_total: Decimal
    actual_total: Decimal
    variance_total: Decimal


def _month_bounds(month: str) -> Tuple[dt.date, dt.date]:
    try:
        y, m = map(int, month.split("-"))
        start = dt.date(y, m, 1)
        end = dt.date(y + (m // 12), (m % 12) + 1, 1) - dt.timedelta(days=1)
        return start, end
    except Exception as e:
        raise HTTPException(status_code=400, detail="month must be 'YYYY-MM'") from e


@router.get("/compare", response_model=BudgetMonthReport)
def compare_month(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
    month: str = Query(..., description="YYYY-MM"),
    account_id: Optional[int] = Query(None),
):
    start_date, end_date = _month_bounds(month)

    # Fetch budgets for month
    budget_rows = session.exec(
        select(Budget.category_id, Budget.amount)
        .where(Budget.user_id == current_user.id, Budget.month == month)
        .order_by(Budget.category_id.asc())
    ).all()
    budget_map: Dict[int, Decimal] = {cid: amt for cid, amt in budget_rows}

    # Actuals by category (sum of txns for that month). Only count debits as spend.
    actual_stmt = (
        select(
            Transaction.category_id,
            func.coalesce(func.sum(Transaction.amount), 0),
        )
        .where(
            Transaction.user_id == current_user.id,
            Transaction.txn_type == "debit",
            Transaction.date >= start_date,
            Transaction.date <= end_date,
        )
        .group_by(Transaction.category_id)
        .order_by(Transaction.category_id.asc())
    )
    if account_id is not None:
        actual_stmt = actual_stmt.where(Transaction.account_id == account_id)

    actual_rows = session.exec(actual_stmt).all()
    actual_map: Dict[Optional[int], Decimal] = {
        cid: Decimal(total) for cid, total in actual_rows
    }

    # Collect all relevant categories (union of budgeted and actual)
    category_ids = set(budget_map.keys()) | {cid for cid in actual_map.keys() if cid is not None}

    # Category names
    categories = {}
    if category_ids:
        q = select(Category.id, Category.name).where(
            Category.user_id == current_user.id, Category.id.in_(category_ids)
        )
        categories = dict(session.exec(q).all())

    totals: List[CategoryBudgetActual] = []
    budget_total = Decimal(0)
    actual_total = Decimal(0)

    for cid in sorted(category_ids):
        budgeted = budget_map.get(cid, Decimal(0))
        actual = actual_map.get(cid, Decimal(0))
        variance = budgeted - actual
        budget_total += budgeted
        actual_total += actual
        totals.append(
            CategoryBudgetActual(
                category_id=cid,
                category_name=categories.get(cid),
                budgeted=budgeted,
                actual=actual,
                variance=variance,
            )
        )

    variance_total = budget_total - actual_total

    return BudgetMonthReport(
        month=month,
        user_id=current_user.id,
        account_id=account_id,
        totals=totals,
        budget_total=budget_total,
        actual_total=actual_total,
        variance_total=variance_total,
    )