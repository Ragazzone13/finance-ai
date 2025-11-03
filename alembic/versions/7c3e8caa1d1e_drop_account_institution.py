"""drop account.institution

Revision ID: 7c3e8caa1d1e
Revises: 03ef697ac9d2
Create Date: 2025-11-02 12:00:00.000000
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "7c3e8caa1d1e"
down_revision = "03ef697ac9d2"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # SQLite-safe batch operation to drop a column
    with op.batch_alter_table("account") as batch_op:
        batch_op.drop_column("institution")


def downgrade() -> None:
    # Re-add the column if rolling back
    with op.batch_alter_table("account") as batch_op:
        batch_op.add_column(sa.Column("institution", sa.String(), nullable=True))