# AuditFlow AI Lite — API

FastAPI + SQLAlchemy + SQLite backend.

## Run

```bash
python3.13 -m venv .venv
.venv/bin/pip install -r requirements.txt
cp .env.example .env                       # optional — defaults are usable as-is
.venv/bin/fastapi dev                       # entrypoint set in pyproject.toml
# or:
.venv/bin/uvicorn app.main:app --reload --port 8765
```

OpenAPI docs available at `http://localhost:8765/docs`.

## Environment

Settings are loaded from `.env` (git-ignored). See `.env.example` for all
variables and their defaults:

| Variable | Default | Purpose |
|---|---|---|
| `APP_ENV` | `development` | `development` \| `test` \| `production` |
| `DATABASE_URL` | `sqlite:///./auditflow.db` | Any SQLAlchemy URL |
| `CORS_ORIGINS` | `http://localhost:5173` | Comma-separated allowed origins |
| `AI_PROVIDER` | `mock` | Recorded in `ai_summary_generated` audit metadata |
| `OPENAI_API_KEY` / `ANTHROPIC_API_KEY` | empty | Reserved for future real-provider work |

`get_settings()` is `@lru_cache`'d. Tests override it via FastAPI's
`dependency_overrides[get_settings]`.

## Tests

```bash
.venv/bin/pytest -q                          # quick run
.venv/bin/pytest --cov=app --cov-report=term # with coverage
.venv/bin/pytest --cov=app --cov-fail-under=80
```

Tests live in `tests/`. Each test gets its own SQLite file under `tmp_path`,
and the app is rebuilt fresh per test via fixtures in `conftest.py` — no
shared state. Models / schemas are excluded from the coverage report (see
`pyproject.toml`).

## Layout

```
app/
  main.py             FastAPI app, CORS, lifespan, route registration
  db.py               Engine, session, Base, init_db
  models/             SQLAlchemy ORM: Batch, BatchRecord, AuditLog
  schemas/            Pydantic v2 request/response models
  routes/             HTTP boundary only — no business logic
  services/
    csv_parser.py            Bytes → list[dict]; raises CsvParseError on bad input
    validation_service.py    list[dict] → list[ValidatedRecord] with duplicate detection
    batch_service.py         Persists batches + per-record validation results
    audit_service.py         Writes and reads audit log entries
    ai_summary_service.py    Deterministic plain-English summary from metrics
    integration_service.py   Mock Salesforce/SharePoint/Monday triggers
```

## Notes

- Database file path comes from `DATABASE_URL`; the default lives at
  `auditflow.db` next to the `app/` package and is ignored by git.
- The `AuditLog` ORM column is named `extra_metadata` because `metadata` is
  reserved on SQLAlchemy's `DeclarativeBase`. It is exposed as `metadata` in
  API responses.
- The "AI" summary is intentionally deterministic. A real LLM call would go in
  `ai_summary_service.generate_summary` and would still only receive aggregate
  metrics — never raw record data. The `AI_PROVIDER` env var is the seam.
