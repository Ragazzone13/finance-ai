# alembic/script.py.mako
"""add indexes and aggregations

Revision ID: a42c9a04be6a
Revises: bc9b1393146e
Create Date: 2025-11-02 09:09:25.042787

"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'a42c9a04be6a'
down_revision = 'bc9b1393146e'
branch_labels = None
depends_on = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass