from sqlmodel import create_engine, Session
from finance_ai.core.config import settings
from finance_ai.db.base import metadata

# For SQLite, check_same_thread=False is often used with async frameworks,
# but here we use standard sync Session so default is fine.
engine = create_engine(settings.DATABASE_URL, echo=False)

def init_db():
    """
    For SQLite dev: create tables automatically.
    For Postgres in prod: use Alembic migrations instead of create_all.
    """
    if settings.DATABASE_URL.startswith("sqlite"):
        metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session