from sqlmodel import SQLModel

# Import models so metadata includes all tables
from finance_ai.db.models import (  # noqa: F401
    User,
    Account,
    Category,
    Transaction,
    Budget,
    Goal,
    Insight,
)

metadata = SQLModel.metadata