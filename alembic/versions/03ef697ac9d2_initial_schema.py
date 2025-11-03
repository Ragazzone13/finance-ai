"""initial schema

Revision ID: 03ef697ac9d2
Revises: None
Create Date: 2025-11-02 00:00:00.000000
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "03ef697ac9d2"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # user
    op.create_table(
        "user",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("email", sa.String(), nullable=False),
        sa.Column("password_hash", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    # You can switch to a UniqueConstraint if you want strict uniqueness
    op.create_index("ix_user_email", "user", ["email"], unique=False)

    # account (with institution initially present; will be dropped by next migration)
    op.create_table(
        "account",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("institution", sa.String(), nullable=True),
        sa.Column("balance", sa.Numeric(18, 2), nullable=False, server_default="0.00"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_account_name", "account", ["name"], unique=False)
    op.create_index("ix_account_user_id", "account", ["user_id"], unique=False)

    # category
    op.create_table(
        "category",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("parent_id", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_category_user_id", "category", ["user_id"], unique=False)
    op.create_index("ix_category_name", "category", ["name"], unique=False)
    op.create_index("ix_category_parent_id", "category", ["parent_id"], unique=False)

    # transaction
    op.create_table(
        "transaction",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("account_id", sa.Integer(), nullable=True),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("amount", sa.Numeric(18, 2), nullable=False),
        sa.Column("txn_type", sa.String(), nullable=False),
        sa.Column("category_id", sa.Integer(), nullable=True),
        sa.Column("vendor", sa.String(), nullable=True),
        sa.Column("note", sa.String(), nullable=True),
        sa.Column("is_recurring", sa.Boolean(), nullable=False, server_default=sa.text("0")),
        sa.Column("source", sa.String(), nullable=False, server_default="manual"),
        sa.Column("hash_key", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_transaction_user_id", "transaction", ["user_id"], unique=False)
    op.create_index("ix_transaction_account_id", "transaction", ["account_id"], unique=False)
    op.create_index("ix_transaction_date", "transaction", ["date"], unique=False)
    op.create_index("ix_transaction_txn_type", "transaction", ["txn_type"], unique=False)
    op.create_index("ix_transaction_category_id", "transaction", ["category_id"], unique=False)
    op.create_index("ix_transaction_vendor", "transaction", ["vendor"], unique=False)
    op.create_index("ix_transaction_source", "transaction", ["source"], unique=False)
    op.create_index("ix_transaction_hash_key", "transaction", ["hash_key"], unique=False)

    # budget
    op.create_table(
        "budget",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("month", sa.String(), nullable=False),
        sa.Column("category_id", sa.Integer(), nullable=False),
        sa.Column("amount", sa.Numeric(18, 2), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_budget_user_id", "budget", ["user_id"], unique=False)
    op.create_index("ix_budget_month", "budget", ["month"], unique=False)
    op.create_index("ix_budget_category_id", "budget", ["category_id"], unique=False)

    # goal
    op.create_table(
        "goal",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("target_amount", sa.Numeric(18, 2), nullable=False),
        sa.Column("target_date", sa.Date(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_goal_user_id", "goal", ["user_id"], unique=False)
    op.create_index("ix_goal_name", "goal", ["name"], unique=False)

    # insight
    op.create_table(
        "insight",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("insight_type", sa.String(), nullable=False),
        sa.Column("payload", sa.String(), nullable=False),
        sa.Column("resolved", sa.Boolean(), nullable=False, server_default=sa.text("0")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_insight_user_id", "insight", ["user_id"], unique=False)
    op.create_index("ix_insight_insight_type", "insight", ["insight_type"], unique=False)

    # Remove server_default set on account.balance after backfill
    with op.batch_alter_table("account") as batch_op:
        batch_op.alter_column("balance", server_default=None)


def downgrade() -> None:
    op.drop_index("ix_insight_insight_type", table_name="insight")
    op.drop_index("ix_insight_user_id", table_name="insight")
    op.drop_table("insight")

    op.drop_index("ix_goal_name", table_name="goal")
    op.drop_index("ix_goal_user_id", table_name="goal")
    op.drop_table("goal")

    op.drop_index("ix_budget_category_id", table_name="budget")
    op.drop_index("ix_budget_month", table_name="budget")
    op.drop_index("ix_budget_user_id", table_name="budget")
    op.drop_table("budget")

    op.drop_index("ix_transaction_hash_key", table_name="transaction")
    op.drop_index("ix_transaction_source", table_name="transaction")
    op.drop_index("ix_transaction_vendor", table_name="transaction")
    op.drop_index("ix_transaction_user_id", table_name="transaction")
    op.drop_index("ix_transaction_txn_type", table_name="transaction")
    op.drop_index("ix_transaction_date", table_name="transaction")
    op.drop_index("ix_transaction_category_id", table_name="transaction")
    op.drop_index("ix_transaction_account_id", table_name="transaction")
    op.drop_table("transaction")

    op.drop_index("ix_category_parent_id", table_name="category")
    op.drop_index("ix_category_name", table_name="category")
    op.drop_index("ix_category_user_id", table_name="category")
    op.drop_table("category")

    op.drop_index("ix_account_user_id", table_name="account")
    op.drop_index("ix_account_name", table_name="account")
    op.drop_table("account")

    op.drop_index("ix_user_email", table_name="user")
    op.drop_table("user")