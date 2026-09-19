"""Database engine/session setup. Uses DATABASE_URL from settings
(defaults to local SQLite for development; point it at a PostgreSQL
DSN in production — the ORM models are dialect-agnostic)."""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from app.models.orm import Base

# Some managed Postgres providers still hand out the legacy "postgres://"
# URL scheme (a holdover from old Heroku conventions). SQLAlchemy 1.4+
# only recognizes "postgresql://" and raises NoSuchModuleError otherwise —
# normalize it here so the app works regardless of which scheme the
# platform's DATABASE_URL uses.
_db_url = settings.DATABASE_URL
if _db_url.startswith("postgres://"):
    _db_url = _db_url.replace("postgres://", "postgresql://", 1)

connect_args = {"check_same_thread": False} if _db_url.startswith("sqlite") else {}
engine = create_engine(_db_url, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
