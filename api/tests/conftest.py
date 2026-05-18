"""Shared pytest fixtures.

Every test gets:
- its own SQLite database (under tmp_path)
- a fresh FastAPI app with overridden settings + DB
- a TestClient bound to that app

No globals are mutated permanently — the engine + session factory are
swapped via app.db.set_engine, and the original is restored on teardown.
"""

from collections.abc import Generator, Iterator
from pathlib import Path

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app import db as db_module
from app.config import Settings, get_settings
from app.db import Base, get_db, make_engine
from app.main import create_app


@pytest.fixture
def tmp_db_url(tmp_path: Path) -> str:
    return f"sqlite:///{tmp_path}/test.db"


@pytest.fixture
def settings(tmp_db_url: str) -> Settings:
    return Settings(
        app_env="test",
        database_url=tmp_db_url,
        cors_origins=["http://testserver"],
        ai_provider="mock",
    )


@pytest.fixture
def app(tmp_db_url: str, settings: Settings) -> Iterator[FastAPI]:
    """Build an isolated FastAPI app pointed at a tmp SQLite DB."""
    previous_engine = db_module._engine
    previous_factory = db_module._session_factory

    engine = make_engine(tmp_db_url)
    db_module.set_engine(engine)
    Base.metadata.create_all(bind=engine)

    application = create_app()
    application.dependency_overrides[get_settings] = lambda: settings

    try:
        yield application
    finally:
        engine.dispose()
        db_module._engine = previous_engine
        db_module._session_factory = previous_factory


@pytest.fixture
def client(app: FastAPI) -> TestClient:
    return TestClient(app)


@pytest.fixture
def db_session(app: FastAPI) -> Generator[Session, None, None]:
    """Open a session against the same engine the app is using."""
    factory = db_module._session_factory
    assert factory is not None, "engine not initialized"
    session = factory()
    try:
        yield session
    finally:
        session.close()


# --- CSV fixture helpers --------------------------------------------------

SAMPLE_GOOD_CSV = (
    "client_name,email,amount,service_type,status,date\n"
    "Acme Inc,ops@acme.com,1500,tax_filing,pending,2026-05-18\n"
    "Beta LLC,books@beta.com,2200,bookkeeping,approved,2026-05-18\n"
)

SAMPLE_MIXED_CSV = (
    "client_name,email,amount,service_type,status,date\n"
    "ABC Corp,finance@abc.com,12000,tax_filing,pending,2026-05-18\n"
    "XYZ LLC,,8000,audit_review,pending,2026-05-18\n"
    "ABC Corp,finance@abc.com,12000,tax_filing,pending,2026-05-18\n"
    "Bad Client,bad@email.com,-500,unknown_service,pending,2026-05-18\n"
)


@pytest.fixture
def good_csv_bytes() -> bytes:
    return SAMPLE_GOOD_CSV.encode("utf-8")


@pytest.fixture
def mixed_csv_bytes() -> bytes:
    return SAMPLE_MIXED_CSV.encode("utf-8")
