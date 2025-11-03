# finance_ai/routers/aggregations.py
from __future__ import annotations

from decimal import Decimal
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlmodel import Session, select, text

from finance_ai.db.models import Account, Transaction, User
from finance_ai.db.session import get_session
from finance_ai.routers.auth import get_current_user

router = APIRouter(prefix="/api/aggregations", tags=["aggregations"])


class CategoryMonthlyTotal(BaseModel):
    category_id: Optional[int]
    category_name: Optional[str]
    total: Decimal


class MonthSummary(BaseModel):
    month: str
    user_id: int
    account_id: Optional[int] = None
    debit_total: Decimal
    credit_total: Decimal
    net_total: Decimal
    by_category: List[CategoryMonthlyTotal]


def _ensure_account_owned(session: Session, user_id: int, account_id: int) -> Account:
    acct = session.get(Account, account_id)
    if not acct or acct.user_id != user_id:
        raise HTTPException(status_code=404, detail="Account not found")
    return acct


@router.get("/monthly", response_model=MonthSummary)
def monthly(
    month: str = Query(..., description="Format YYYY-MM"),
    account_id: Optional[int] = Query(None),
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    if account_id:
        _ensure_account_owned(session, current_user.id, account_id)

    month_like = f"{month}-%"

    base = select(Transaction).join(Account).where(
        Account.user_id == current_user.id,
        Transaction.occurred_on.like(month_like),
    )
    if account_id:
        base = base.where(Transaction.account_id == account_id)

    # Totals by type
    debit_total = Decimal(
        session.exec(
            select(text("COALESCE(SUM(amount), 0)"))
            .select_from(base.subquery())
            .where(text("type = 'debit'"))
        ).first() or 0
    )
    credit_total = Decimal(
        session.exec(
            select(text("COALESCE(SUM(amount), 0)"))
            .select_from(base.subquery())
            .where(text("type = 'credit'"))
        ).first() or 0
    )

    # Group by category (category_name placeholder unless you join categories)
    rows = session.exec(
        select(
            Transaction.category_id,
            text("COALESCE(SUM(amount), 0) AS total"),
            text("NULL AS category_name"),
        )
        .select_from(base.subquery())
        .group_by(Transaction.category_id)
    ).all()

    by_category: List[CategoryMonthlyTotal] = []
    for category_id, total, category_name in rows:
        by_category.append(
            CategoryMonthlyTotal(
                category_id=category_id,
                category_name=category_name,
                total=Decimal(total),
            )
        )

    net_total = credit_total - debit_total
    return MonthSummary(
        month=month,
        user_id=current_user.id,
        account_id=account_id,
        debit_total=debit_total,
        credit_total=credit_total,
        net_total=net_total,
        by_category=by_category,
    )