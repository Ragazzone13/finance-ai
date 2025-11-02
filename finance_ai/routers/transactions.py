from __future__ import annotations

from typing import List

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlmodel import Session, select

from finance_ai.db.session import get_session
from finance_ai.db.models import Transaction
from finance_ai.schemas.transactions import TransactionCreate, TransactionRead
from finance_ai.services.csv_import import parse_transactions_csv
from sqlalchemy import desc

router = APIRouter()


@router.get("", response_model=List[TransactionRead])
def list_transactions(user_id: int, session: Session = Depends(get_session)) -> List[Transaction]:
    stmt = (
        select(Transaction)
        .where(Transaction.user_id == user_id)
        .order_by(desc(Transaction.date))
    )
    results = session.exec(stmt).all()
    return results


@router.post("", response_model=TransactionRead)
def create_transaction(payload: TransactionCreate, session: Session = Depends(get_session)) -> Transaction:
    data = payload.model_dump()
    t = Transaction(**data)

    if getattr(t, "txn_type", None) not in ("debit", "credit"):
        raise HTTPException(status_code=400, detail="txn_type must be 'debit' or 'credit'")

    if not t.hash_key:
        t.hash_key = f"{t.user_id}:{t.date.isoformat()}:{t.amount}:{t.txn_type}:{t.vendor or ''}"

    session.add(t)
    session.commit()
    session.refresh(t)
    return t


@router.post("/import")
def import_transactions_csv(
    user_id: int,
    file: UploadFile = File(...),
    session: Session = Depends(get_session),
) -> dict:
    try:
        items = parse_transactions_csv(user_id, file.file)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"CSV parse error: {e}")

    created = 0
    for item in items:
        # Map incoming 'type' to 'txn_type' if needed
        if "type" in item and "txn_type" not in item:
            item["txn_type"] = item.pop("type")

        t = Transaction(**item)

        if not t.hash_key:
            t.hash_key = f"{t.user_id}:{t.date.isoformat()}:{t.amount}:{t.txn_type}:{t.vendor or ''}"

        exists = session.exec(
            select(Transaction).where(Transaction.hash_key == t.hash_key)
        ).first()
        if exists:
            continue

        session.add(t)
        created += 1

    session.commit()
    return {"imported": created}