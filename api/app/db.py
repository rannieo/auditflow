"""SQLAlchemy engine, session, and Base — configurable via Settings.

The default engine/session are lazily built from ``get_settings()`` so tests
can swap them out with ``set_engine(make_engine(...))`` (or via FastAPI's
``dependency_overrides[get_db]``) without monkey-patching.
"""

from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.config import get_settings


class Base(DeclarativeBase):
    pass


def make_engine(url: str) -> Engine:
    """Build an Engine with SQLite-safe defaults."""
    connect_args = {"check_same_thread": False} if url.startswith("sqlite") else {}
    return create_engine(url, connect_args=connect_args, future=True)


_engine: Engine | None = None
_session_factory: sessionmaker[Session] | None = None


def _ensure_engine() -> tuple[Engine, sessionmaker[Session]]:
    global _engine, _session_factory
    if _engine is None or _session_factory is None:
        _engine = make_engine(get_settings().database_url)
        _session_factory = sessionmaker(
            bind=_engine, autoflush=False, autocommit=False, future=True
        )
    return _engine, _session_factory


def set_engine(engine: Engine) -> None:
    """Replace the process-wide engine + session factory (used by tests)."""
    global _engine, _session_factory
    _engine = engine
    _session_factory = sessionmaker(
        bind=engine, autoflush=False, autocommit=False, future=True
    )


def get_engine() -> Engine:
    engine, _ = _ensure_engine()
    return engine


def get_db() -> Generator[Session, None, None]:
    _, factory = _ensure_engine()
    db = factory()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    # Import models so they're registered on Base before create_all.
    from app.models import audit_log, batch, batch_record  # noqa: F401

    Base.metadata.create_all(bind=get_engine())
