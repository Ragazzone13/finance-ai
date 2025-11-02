# alembic/script.py.mako
"""indexes improvements

Revision ID: bc9b1393146e
Revises: f3db4c6104b5
Create Date: 2025-11-02 09:08:05.417899

"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'bc9b1393146e'
down_revision = 'f3db4c6104b5'
branch_labels = None
depends_on = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass