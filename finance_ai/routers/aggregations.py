# finance_ai/routers/aggregations.py
from __future__ import annotations

import datetime as dt
from decimal import Decimal
from typing import List, Optional, Tuple

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import func
from sqlmodel import Session, select

from finance_ai.db.models import Transaction, Category, User
from finance_ai.db.session import get_session
from finance_ai.deps.users import get_current_user

router = APIRouter(prefix="/api/aggregations", tags=["aggregations"])


class CategoryMonthlyTotal(BaseModel):
    category_id: Optional[int]
    category_name: Optional[str]
    total: Decimal


class MonthSummary(BaseModel):
    month: str  # "YYYY-MM"
    user_id: int
    account_id: Optional[int]
    debit_total: Decimal
    credit_total: Decimal
    net_total: Decimal
    by_category: List[CategoryMonthlyTotal]


def _month_bounds(month: str) -> Tuple[dt.date, dt.date]:
    try:
        year, mon = month.split("-")
        y = int(year)
        m = int(mon)
        start = dt.date(y, m, 1)
        if m == 12:
            end = dt.date(y + 1, 1, 1) - dt.timedelta(days=1)
        else:
            end = dt.date(y, m + 1, 1) - dt.timedelta(days=1)
        return start, end
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid month format: {month}. Use YYYY-MM") from e


@router.get("/monthly", response_model=MonthSummary)
def monthly_summary(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
    month: str = Query(..., description="Format YYYY-MM"),
    account_id: Optional[int] = Query(None),
):
    start_date, end_date = _month_bounds(month)

    # Debit total
    debit_stmt = select(func.coalesce(func.sum(Transaction.amount), 0)).where(
        Transaction.user_id == current_user.id,
        Transaction.txn_type == "debit",
        Transaction.date >= start_date,
        Transaction.date <= end_date,
    )
    if account_id is not None:
        debit_stmt = debit_stmt.where(Transaction.account_id == account_id)
    debit_total: Decimal = session.exec(debit_stmt).one()[0]  # type: ignore

    # Credit total
    credit_stmt = select(func.coalesce(func.sum(Transaction.amount), 0)).where(
        Transaction.user_id == current_user.id,
        Transaction.txn_type == "credit",
        Transaction.date >= start_date,
        Transaction.date <= end_date,
    )
    if account_id is not None:
        credit_stmt = credit_stmt.where(Transaction.account_id == account_id)
    credit_total: Decimal = session.exec(credit_stmt).one()[0]  # type: ignore

    # By category
    cat_stmt = (
        select(
            Transaction.category_id,
            func.coalesce(func.sum(Transaction.amount), 0).label("total"),
            Category.name,
        )
        .join(Category, Category.id == Transaction.category_id, isouter=True)
        .where(
            Transaction.user_id == current_user.id,
            Transaction.date >= start_date,
            Transaction.date <= end_date,
        )
        .group_by(Transaction.category_id, Category.name)
        .order_by(func.coalesce(func.sum(Transaction.amount), 0).desc())
    )
    if account_id is not None:
        cat_stmt = cat_stmt.where(Transaction.account_id == account_id)

    rows = session.exec(cat_stmt).all()

    by_category: List[CategoryMonthlyTotal] = []
    for category_id, total, category_name in rows:
        by_category.append(
            CategoryMonthlyTotal(
                category_id=category_id,
                category_name=category_name,
                total=Decimal(total),
            )
        )

    net_total = (credit_total or Decimal(0)) - (debit_total or Decimal(0))
    return MonthSummary(
        month=month,
        user_id=current_user.id,
        account_id=account_id,
        debit_total=Decimal(debit_total),
        credit_total=Decimal(credit_total),
        net_total=Decimal(net_total),
        by_category=by_category,
    )