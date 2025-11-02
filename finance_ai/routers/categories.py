# finance_ai/routers/categories.py
from __future__ import annotations

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, field_validator
from sqlmodel import Session, select

from finance_ai.db.models import Category, User
from finance_ai.db.session import get_session
from finance_ai.deps.users import get_current_user

router = APIRouter(prefix="/api/categories", tags=["categories"])


class CategoryCreate(BaseModel):
    name: str
    parent_id: Optional[int] = None

    @field_validator("name")
    @classmethod
    def name_not_empty(cls, v: str) -> str:
        v2 = v.strip()
        if not v2:
            raise ValueError("name cannot be empty")
        return v2


class CategoryUpdate(BaseModel):
    name: Optional[str] = None
    parent_id: Optional[int] = None


class CategoryRead(BaseModel):
    id: int
    user_id: int
    name: str
    parent_id: Optional[int]

    class Config:
        from_attributes = True


@router.post("", response_model=CategoryRead, status_code=201)
def create_category(
    payload: CategoryCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    # Ensure parent belongs to same user if provided
    if payload.parent_id is not None:
        parent = session.get(Category, payload.parent_id)
        if not parent or parent.user_id != current_user.id:
            raise HTTPException(status_code=400, detail="Invalid parent_id for user")

    cat = Category(user_id=current_user.id, **payload.model_dump())
    session.add(cat)
    session.commit()
    session.refresh(cat)
    return cat


@router.get("", response_model=List[CategoryRead])
def list_categories(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
    name: Optional[str] = Query(None),
    parent_id: Optional[int] = Query(None),
    limit: int = Query(200, ge=1, le=1000),
    offset: int = Query(0, ge=0),
):
    stmt = select(Category).where(Category.user_id == current_user.id)
    if name:
        stmt = stmt.where(Category.name == name)
    if parent_id is not None:
        stmt = stmt.where(Category.parent_id == parent_id)
    stmt = stmt.order_by(Category.name.asc(), Category.id.asc()).limit(limit).offset(offset)
    rows = session.exec(stmt).all()
    return rows


@router.get("/{category_id}", response_model=CategoryRead)
def get_category(
    category_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    cat = session.get(Category, category_id)
    if not cat or cat.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Category not found")
    return cat


@router.patch("/{category_id}", response_model=CategoryRead)
def update_category(
    category_id: int,
    payload: CategoryUpdate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    cat = session.get(Category, category_id)
    if not cat or cat.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Category not found")

    data = payload.model_dump(exclude_unset=True)

    # Validate parent change
    if "parent_id" in data and data["parent_id"] is not None:
        parent = session.get(Category, data["parent_id"])
        if not parent or parent.user_id != current_user.id:
            raise HTTPException(status_code=400, detail="Invalid parent_id for user")
        if data["parent_id"] == category_id:
            raise HTTPException(status_code=400, detail="Category cannot be its own parent")

    for k, v in data.items():
        setattr(cat, k, v)

    session.add(cat)
    session.commit()
    session.refresh(cat)
    return cat


@router.delete("/{category_id}", status_code=204)
def delete_category(
    category_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    cat = session.get(Category, category_id)
    if not cat or cat.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Category not found")

    sub = session.exec(select(Category).where(Category.parent_id == category_id)).first()
    if sub:
        raise HTTPException(
            status_code=400, detail="Cannot delete a category that has subcategories"
        )

    session.delete(cat)
    session.commit()
    return None