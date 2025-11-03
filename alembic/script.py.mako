"""${message}

Revision ID: ${up_revision}
Revises: ${down_revision | comma,n}
Create Date: ${create_date}

"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa
${imports if imports else ""}

# IMPORTANT: Avoid SQLModel-specific types in migrations.
# If autogenerate ever tries to emit sqlmodel.sql.sqltypes.AutoString,
# fall back to sa.String by aliasing at runtime.
try:
    import sqlmodel  # noqa: F401
    # Defensive alias: if AutoString is referenced, map it to sa.String
    AutoString = sa.String  # noqa: N816
except Exception:  # pragma: no cover
    AutoString = sa.String  # noqa: N816

# revision identifiers, used by Alembic.
revision = ${repr(up_revision)}
down_revision = ${repr(down_revision) if down_revision else None}
branch_labels = ${repr(branch_labels) if branch_labels else None}
depends_on = ${repr(depends_on) if depends_on else None}


def upgrade() -> None:
    ${upgrades if upgrades else "pass"}


def downgrade() -> None:
    ${downgrades if downgrades else "pass"}