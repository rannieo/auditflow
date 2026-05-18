# AuditFlow AI Lite — development convenience targets.
#
# Quick start:
#   make install          # one-time: create venv + install deps for both apps
#   make dev              # run API (:8765) and web (:5173) together — Ctrl+C stops both
#
# Individual servers (useful in separate terminals):
#   make api              # FastAPI with --reload
#   make web              # Vite dev server

PYTHON           ?= python3.13
API_DIR          := api
WEB_DIR          := web
API_PORT         ?= 8765
WEB_PORT         ?= 5173
VENV             := $(API_DIR)/.venv
VENV_PY          := $(VENV)/bin/python
VENV_PIP         := $(VENV)/bin/pip
VENV_UVICORN     := $(VENV)/bin/uvicorn

.PHONY: help install install-api install-web dev api web stop

help:
	@echo "AuditFlow AI Lite — make targets"
	@echo ""
	@echo "  make install      Install dependencies for both apps."
	@echo "  make dev          Run both servers (API :$(API_PORT), web :$(WEB_PORT))."
	@echo "  make api          Run only the FastAPI server."
	@echo "  make web          Run only the Vite dev server."
	@echo "  make stop         Best-effort kill of anything still listening on $(API_PORT)/$(WEB_PORT)."

# ---- Installation -----------------------------------------------------------

install: install-api install-web

install-api: $(VENV_PY)
	$(VENV_PIP) install -q --upgrade pip
	$(VENV_PIP) install -q -r $(API_DIR)/requirements.txt

$(VENV_PY):
	$(PYTHON) -m venv $(VENV)

install-web: $(WEB_DIR)/node_modules

$(WEB_DIR)/node_modules: $(WEB_DIR)/package.json
	cd $(WEB_DIR) && npm install --silent

# ---- Dev servers ------------------------------------------------------------

# Run both servers. The `trap` line makes Ctrl+C kill the whole process
# group so neither server is left orphaned. `wait` blocks the parent until
# both children exit.
dev: install
	@echo "▶ API  http://127.0.0.1:$(API_PORT)   docs: /docs"
	@echo "▶ Web  http://localhost:$(WEB_PORT)"
	@echo "Press Ctrl+C to stop both."
	@trap 'kill 0' INT TERM EXIT; \
	  ( cd $(API_DIR) && .venv/bin/uvicorn app.main:app --reload --host 127.0.0.1 --port $(API_PORT) ) & \
	  ( cd $(WEB_DIR) && npm run dev -- --port $(WEB_PORT) --strictPort ) & \
	  wait

api: install-api
	cd $(API_DIR) && .venv/bin/uvicorn app.main:app --reload --host 127.0.0.1 --port $(API_PORT)

web: install-web
	cd $(WEB_DIR) && npm run dev -- --port $(WEB_PORT) --strictPort

stop:
	-@lsof -ti tcp:$(API_PORT) | xargs kill 2>/dev/null || true
	-@lsof -ti tcp:$(WEB_PORT) | xargs kill 2>/dev/null || true
	@echo "Stopped (if anything was listening on $(API_PORT)/$(WEB_PORT))."
