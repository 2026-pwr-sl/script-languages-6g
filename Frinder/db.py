from functools import lru_cache
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from db_models import Base

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
DATABASE_FILE = DATA_DIR / "frinder.db"

@lru_cache(maxsize=1)
def _engine():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    engine = create_engine(f"sqlite:///{DATABASE_FILE.as_posix()}", future=True)
    Base.metadata.create_all(engine)
    return engine


@lru_cache(maxsize=1)
def _session_factory():
    return sessionmaker(bind=_engine(), future=True)


def _session():
    return _session_factory()()


def session():
    return _session()
