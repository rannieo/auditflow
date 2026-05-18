# AuditFlow AI Lite — Web

React 19 + TypeScript + Vite 8 + Tailwind v4. Hand-rolled components in
shadcn/ui shape (no `shadcn init` — fewer moving parts for an MVP).

## Run

```bash
npm install
cp .env.example .env.local         # optional — defaults work as-is
npm run dev                         # http://localhost:5173
npm run build                       # production bundle
```

Vite proxies `/api/*` to `http://127.0.0.1:8765`, so start the FastAPI server
first or set up your own proxy target in `vite.config.ts`.

## Environment

Vite exposes only `VITE_*` variables to the client. Edit `.env.local` (git-ignored):

| Variable | Default | Purpose |
|---|---|---|
| `VITE_API_BASE_URL` | `/api` | Leave as `/api` in dev so requests go through the Vite proxy. Set to a full origin in production. |
| `VITE_APP_TITLE` | `AuditFlow AI Lite` | Displayed in the header. |

All env access goes through `src/env.ts`. Never put secrets here — anything
`VITE_*` ships to the browser.

## Tests

```bash
npm test           # watch mode
npm run test:run   # one-shot
npm run test:cov   # one-shot + coverage report
```

Tests use **Vitest** (jsdom), **React Testing Library**, and **MSW** for
API mocking. Default handlers live in `src/test/handlers.ts`; individual
tests use `server.use(http.get(...))` to override them per case.

## Layout

```
src/
  App.tsx             Header, tab nav, page switching
  main.tsx            React entry
  index.css           Tailwind import + @theme tokens + Inter font
  lib/utils.ts        cn() — clsx + tailwind-merge
  api/
    client.ts         fetch wrappers
    types.ts          BatchSummary, BatchRecord, AuditLog, ...
    batches.ts        upload, getBatchDetail, generateAiSummary, triggerIntegration
    auditLogs.ts      listAuditLogs
  components/
    ui/               Button, Card, Table, Badge — small Tailwind primitives
    UploadCsvCard.tsx
    BatchSummaryCards.tsx
    ValidationResultsTable.tsx
    AiSummaryPanel.tsx
    MockIntegrationActions.tsx
    AuditLogTable.tsx
  pages/
    DashboardPage.tsx
    AuditLogsPage.tsx
```

## Design

Palette and typography come from the **Data-Dense Dashboard** profile of the
`ui-ux-pro-max` skill — navy primary (`#1e3a5f`), emerald accent (`#059669`),
neutral slate background, and Inter for both display and body text. The look
is deliberately quiet: no gradients, no hero, no icon clutter.

Validation rows use subtle tints (rose-50/40 for failed, amber-50/40 for
duplicate) so the table stays scannable without aggressive coloring.
