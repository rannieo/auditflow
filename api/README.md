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
| `AI_PROVIDER` | `mock` | `mock` (deterministic, no network) or `ollama` (Ollama Cloud) |
| `OLLAMA_API_KEY` | empty | Required when `AI_PROVIDER=ollama`; get one at https://ollama.com/settings/keys |
| `OLLAMA_BASE_URL` | `https://ollama.com` | Cloud API base; override for self-hosted |
| `OLLAMA_MODEL` | `gpt-oss:120b-cloud` | Model tag (see model note below) |
| `OLLAMA_TIMEOUT_SECONDS` | `30` | Outbound request timeout |
| `OPENAI_API_KEY` / `ANTHROPIC_API_KEY` | empty | Reserved for future real-provider work |

### AI summary provider

The `/api/batches/{id}/ai-summary` route is provider-agnostic: it dispatches
to a small `AiProvider` Protocol with two implementations today —
`MockProvider` and `OllamaProvider`. The mock is fully deterministic and
makes no network calls; the Ollama provider calls
`POST https://ollama.com/api/chat` with a Bearer token.

**Privacy contract.** Both providers receive a `BatchMetrics` dataclass
containing only aggregate counts (total / passed / failed / duplicate),
top friendly failure-reason labels, and the filename. Raw `client_name`,
`email`, `amount`, and `date` values are *never* reachable from a
provider. A regression test (`test_ai_providers.py
::test_ollama_request_does_not_leak_pii_fields`) asserts this on every CI run.

**Resilience.** Any provider failure (4xx/5xx/timeout/network/malformed
response) silently falls back to the mock summary. The user always gets
a response; the audit log records `status=degraded`, `fallback_from`,
and a truncated error.

**Logging.** Every Ollama call emits structured INFO/WARNING log lines
to stdout (visible under `make dev` / `fastapi dev`). API keys are never
logged. Long responses are truncated at 2000 chars.

```
ollama_request    model=gpt-oss:120b-cloud url=https://ollama.com/api/chat
ollama_response   status=200 latency_ms=842 content_chars=312 content=<summary…>
ollama_error      status=500 latency_ms=120 body={"error":"…"}
ollama_transport_error  latency_ms=30000 error=TimeoutException(…)
```

**Model name note.** Per the official docs, `gpt-oss:120b-cloud` is the
tag for a *local* Ollama daemon that offloads to cloud, while
`gpt-oss:120b` is the direct-cloud-API tag. We default to
`gpt-oss:120b-cloud` per the project's preference; switch to
`gpt-oss:120b` via `OLLAMA_MODEL` if the docs' distinction matters.

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
