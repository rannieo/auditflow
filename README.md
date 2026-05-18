# AuditFlow AI Lite

A small internal-tool MVP for a CPA / financial-advisory workflow: upload a CSV
of client service records, validate them, see passed / failed / duplicate
results, generate a plain-English summary of the issues, fire mock downstream
integrations, and review an audit log of everything that happened.

> This is not intended to be a full compliance product. It is a focused
> portfolio project showing how I approach internal application delivery: clear
> API boundaries, simple architecture, traceability, validation, and
> production-ready thinking.

## Why it exists

CPA and financial-advisory teams often live between Excel, Salesforce,
SharePoint, and ad-hoc scripts. The first thing that goes wrong at scale is
data quality. This MVP demonstrates a tool a small team could actually use day
one — ingest, validate, summarize, sync — and the architecture path to grow
into a hardened internal product.

## Tech stack

- **Backend** — Python 3.13, FastAPI 0.115, SQLAlchemy 2, Pydantic 2, SQLite
- **Frontend** — React 19 + TypeScript, Vite 8, Tailwind CSS v4, shadcn-style
  components (hand-rolled, Radix-free except for `@radix-ui/react-slot`)
- **Sample data** — `sample-data/client-services-sample.csv`

## Features

- CSV upload with header validation
- Per-record validation against a fixed set of business rules
- Duplicate detection across a batch (`client_name + email + amount + service_type`)
- Batch summary metrics (total / passed / failed / duplicate)
- AI summary backed by Ollama Cloud (`gpt-oss:120b-cloud`) when `AI_PROVIDER=ollama` + `OLLAMA_API_KEY` is set; deterministic mock otherwise — demo works with no key
- Mock integrations for Salesforce, SharePoint, and Monday.com
- Audit log that records every meaningful action with metadata

## Local setup

Each app owns its own env file. Copy the examples on first run — defaults work
as-is for local dev:

```bash
cp api/.env.example api/.env
cp web/.env.example web/.env.local
```

### API

```bash
cd api
python3.13 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/fastapi dev   # or: .venv/bin/uvicorn app.main:app --reload --port 8765
```

The SQLite database is created at `api/auditflow.db` on first request.

### Web

```bash
cd web
npm install
npm run dev
```

The Vite dev server runs on `http://localhost:5173` and proxies `/api/*` to the
FastAPI server on port 8765.

## Tests

```bash
cd api && .venv/bin/pytest                       # 46 tests, ~93% coverage
cd web && npm run test:run                       # 29 tests, ~93% coverage
```

See each app's README for env / coverage flags.

## Sample CSV usage

```bash
curl -X POST http://localhost:8765/api/batches/upload \
  -F "file=@sample-data/client-services-sample.csv"
```

You can also drop `sample-data/client-services-sample.csv` into the upload
field on the dashboard.

## API endpoints

| Method | Path | Purpose |
|---|---|---|
| `GET` | `/api/health` | Liveness probe |
| `POST` | `/api/batches/upload` | Upload + validate a CSV (multipart `file`) |
| `GET` | `/api/batches/{batch_id}` | Batch summary + per-record results |
| `POST` | `/api/batches/{batch_id}/ai-summary` | Generate plain-English summary |
| `POST` | `/api/batches/{batch_id}/integrations/{name}` | Mock sync (`salesforce` \| `sharepoint` \| `monday`) |
| `GET` | `/api/audit-logs` | Latest audit entries, newest first |

## Architecture notes

```
api/app/
  main.py                — FastAPI app + lifespan
  db.py                  — SQLAlchemy engine + session
  models/                — Batch, BatchRecord, AuditLog
  schemas/               — Pydantic request/response shapes
  routes/                — HTTP boundary; no business logic
  services/              — csv_parser, validation, batch, audit, ai_summary, integration
```

Validation rules are isolated in `services/validation_service.py` and tested
in-isolation simply because they're a pure function over a list of dicts.

The frontend mirrors the backend's narrow boundaries:

```
web/src/
  api/                   — typed client + per-resource modules
  components/            — feature components (one per card on the dashboard)
  components/ui/         — small primitives (Button, Card, Table, Badge)
  pages/                 — DashboardPage, AuditLogsPage
  lib/utils.ts           — cn() helper
```

## Production evolution

How the local MVP maps to a hardened Azure deployment:

| MVP | Production equivalent |
|---|---|
| SQLite | Azure SQL |
| FastAPI local server | Azure Container Apps |
| Local REST API | Azure API Management |
| Mock auth (none) | Entra ID / OAuth2 |
| Local logs | Azure Monitor / Application Insights |
| Mock integrations | Salesforce, SharePoint (Microsoft Graph), Monday.com APIs |
| Local env vars | Azure Key Vault |

## Honest MVP limitations

- No authentication. Every request is "demo-user".
- The AI summary supports two providers behind an `AiProvider` Protocol:
  a deterministic `MockProvider` (default) and an `OllamaProvider` that calls
  the Ollama Cloud hosted API. Switch via `AI_PROVIDER=ollama` +
  `OLLAMA_API_KEY`. Either way only aggregate metrics are sent — never raw
  record values. See `api/README.md` for the privacy contract.
- Integrations are all mocked. Each click writes an audit log entry but no
  network calls are made.
- No RBAC, multi-tenancy, retention policies, or schema versioning.
- No real tests yet, though every service is structured to be unit-testable
  without a server.
- SQLite is single-writer; fine for the demo, not for concurrent users.

## Demo script

1. Open the app at `http://localhost:5173`.
2. Upload `sample-data/client-services-sample.csv`.
3. Note the four summary cards — 4 total, 0 passed, 2 failed, 2 duplicate.
4. Scroll to the validation table and inspect per-row issues.
5. Click **Generate AI summary** — the panel fills with a plain-English review.
6. Click **Sync to Salesforce** (or another integration).
7. Switch to the **Audit log** tab — every action above is recorded.
