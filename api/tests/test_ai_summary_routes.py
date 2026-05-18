"""Integration tests for POST /api/batches/{batch_id}/ai-summary."""

import json

import httpx
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.deps import get_ai_provider
from app.models.audit_log import AuditLog
from app.services.ai_providers.ollama_provider import OllamaProvider


def _upload(client: TestClient, content: bytes):
    return client.post(
        "/api/batches/upload",
        files={"file": ("sample.csv", content, "text/csv")},
    )


def _use_ollama_with_handler(app: FastAPI, handler) -> None:
    """Override the AI provider dep so the route's Ollama call hits ``handler``."""
    def _factory() -> httpx.Client:
        return httpx.Client(transport=httpx.MockTransport(handler))

    def _provider() -> OllamaProvider:
        return OllamaProvider(
            api_key="test-key",
            base_url="https://ollama.example",
            model="gpt-oss:120b-cloud",
            timeout=5.0,
            http_client_factory=_factory,
        )

    app.dependency_overrides[get_ai_provider] = _provider


def test_ai_summary_returns_non_empty_string(
    client: TestClient, mixed_csv_bytes: bytes
) -> None:
    batch_id = _upload(client, mixed_csv_bytes).json()["batch_id"]

    response = client.post(f"/api/batches/{batch_id}/ai-summary")

    assert response.status_code == 200
    assert response.json()["summary"].strip() != ""


def test_ai_summary_mentions_batch_counts(
    client: TestClient, mixed_csv_bytes: bytes
) -> None:
    batch_id = _upload(client, mixed_csv_bytes).json()["batch_id"]

    summary = client.post(f"/api/batches/{batch_id}/ai-summary").json()["summary"]

    # mixed_csv has 4 total / 0 passed / 2 failed / 2 duplicate
    assert "4" in summary
    assert "2 failed" in summary
    assert "2 duplicate" in summary


def test_ai_summary_writes_audit_log_entry(
    client: TestClient, db_session: Session, mixed_csv_bytes: bytes
) -> None:
    batch_id = _upload(client, mixed_csv_bytes).json()["batch_id"]

    client.post(f"/api/batches/{batch_id}/ai-summary")

    entries = (
        db_session.query(AuditLog)
        .filter(AuditLog.action == "ai_summary_generated")
        .all()
    )
    assert len(entries) == 1
    meta = json.loads(entries[0].extra_metadata)
    assert meta["batch_id"] == batch_id
    assert meta["provider"] == "mock"


def test_ai_summary_with_unknown_batch_returns_404(client: TestClient) -> None:
    response = client.post("/api/batches/no-such-batch/ai-summary")

    assert response.status_code == 404


# --- Ollama provider integration -------------------------------------------


def test_ai_summary_with_ollama_returns_provider_text_and_stamps_audit(
    client: TestClient, app, db_session: Session, mixed_csv_bytes: bytes
) -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json={
                "message": {
                    "role": "assistant",
                    "content": "Cloud-generated summary.",
                }
            },
        )

    _use_ollama_with_handler(app, handler)
    batch_id = _upload(client, mixed_csv_bytes).json()["batch_id"]

    response = client.post(f"/api/batches/{batch_id}/ai-summary")

    assert response.status_code == 200
    assert response.json()["summary"] == "Cloud-generated summary."

    entry = (
        db_session.query(AuditLog)
        .filter(AuditLog.action == "ai_summary_generated")
        .one()
    )
    meta = json.loads(entry.extra_metadata)
    assert meta["provider"] == "ollama"
    assert meta["model"] == "gpt-oss:120b-cloud"
    assert "latency_ms" in meta
    assert entry.status == "success"


def test_ai_summary_with_ollama_500_falls_back_to_mock_and_audits_degraded(
    client: TestClient, app, db_session: Session, mixed_csv_bytes: bytes
) -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(500, json={"error": "boom"})

    _use_ollama_with_handler(app, handler)
    batch_id = _upload(client, mixed_csv_bytes).json()["batch_id"]

    response = client.post(f"/api/batches/{batch_id}/ai-summary")

    assert response.status_code == 200
    # Mock fallback summary mentions counts from the mixed CSV.
    assert "4 record" in response.json()["summary"]

    entry = (
        db_session.query(AuditLog)
        .filter(AuditLog.action == "ai_summary_generated")
        .one()
    )
    assert entry.status == "degraded"
    meta = json.loads(entry.extra_metadata)
    assert meta["provider"] == "mock"
    assert meta["fallback_from"] == "ollama"
    assert "provider_error" in meta


def test_ai_summary_with_ollama_timeout_falls_back_to_mock(
    client: TestClient, app, db_session: Session, mixed_csv_bytes: bytes
) -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.TimeoutException("simulated timeout")

    _use_ollama_with_handler(app, handler)
    batch_id = _upload(client, mixed_csv_bytes).json()["batch_id"]

    response = client.post(f"/api/batches/{batch_id}/ai-summary")

    assert response.status_code == 200
    entry = (
        db_session.query(AuditLog)
        .filter(AuditLog.action == "ai_summary_generated")
        .one()
    )
    assert entry.status == "degraded"
    meta = json.loads(entry.extra_metadata)
    assert meta["fallback_from"] == "ollama"
    assert "Timeout" in meta["provider_error"]
