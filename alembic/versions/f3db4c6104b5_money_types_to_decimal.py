# alembic/script.py.mako
"""money types to Decimal

Revision ID: f3db4c6104b5
Revises: 2043da5cd525
Create Date: 2025-11-02 09:04:28.086184

"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'f3db4c6104b5'
down_revision = '2043da5cd525'
branch_labels = None
depends_on = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass