from datetime import date
from typing import Optional
from pydantic import BaseModel, field_validator

class TransactionCreate(BaseModel):
    user_id: int
    account_id: Optional[int] = None
    date: date
    amount: float
    txn_type: str  # "debit" | "credit"
    category_id: Optional[int] = None
    vendor: Optional[str] = None
    note: Optional[str] = None
    is_recurring: bool = False
    source: str = "manual"

    @field_validator("txn_type")
    @classmethod
    def validate_type(cls, v: str):
        v = v.lower().strip()
        if v not in {"debit", "credit"}:
            raise ValueError("txn_type must be 'debit' or 'credit'")
        return v

class TransactionRead(BaseModel):
    id: int
    user_id: int
    account_id: Optional[int]
    date: date
    amount: float
    txn_type: str
    category_id: Optional[int]
    vendor: Optional[str]
    note: Optional[str]
    is_recurring: bool
    source: str

    class Config:
        from_attributes = True