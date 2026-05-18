"""Integration tests for POST /api/batches/{batch_id}/ai-summary."""

import json

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.audit_log import AuditLog


def _upload(client: TestClient, content: bytes):
    return client.post(
        "/api/batches/upload",
        files={"file": ("sample.csv", content, "text/csv")},
    )


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
