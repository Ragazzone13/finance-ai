# alembic/versions/10b107c6846d_add_unique_index_to_users_email.py
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "10b107c6846d"
down_revision = "82f071be41f1"  # keep your actual previous id
branch_labels = None
depends_on = None

INDEX_NAME = "uq_users_email"
TABLE_NAME = "user"  # singular, from your SQLModel default


def upgrade() -> None:
    # Create a unique index on user(email). SQLite-friendly.
    op.create_index(INDEX_NAME, TABLE_NAME, ["email"], unique=True)


def downgrade() -> None:
    op.drop_index(INDEX_NAME, table_name=TABLE_NAME)