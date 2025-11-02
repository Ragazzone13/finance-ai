from __future__ import annotations
from sqlmodel import SQLModel

# Import models to register tables with SQLModel metadata
from finance_ai.db import models  # noqa: F401

metadata = SQLModel.metadata