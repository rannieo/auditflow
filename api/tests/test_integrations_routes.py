"""Integration tests for POST /api/batches/{batch_id}/integrations/{name}."""

import json

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.audit_log import AuditLog


def _upload(client: TestClient, content: bytes) -> str:
    return client.post(
        "/api/batches/upload",
        files={"file": ("sample.csv", content, "text/csv")},
    ).json()["batch_id"]


@pytest.mark.parametrize(
    "name,expected_message,expected_action",
    [
        ("salesforce", "Salesforce", "integration_salesforce_triggered"),
        ("sharepoint", "SharePoint", "integration_sharepoint_triggered"),
        ("monday", "Monday.com", "integration_monday_triggered"),
    ],
)
def test_trigger_known_integration_returns_success(
    client: TestClient,
    db_session: Session,
    mixed_csv_bytes: bytes,
    name: str,
    expected_message: str,
    expected_action: str,
) -> None:
    batch_id = _upload(client, mixed_csv_bytes)

    response = client.post(f"/api/batches/{batch_id}/integrations/{name}")

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "success"
    assert expected_message in body["message"]

    # Audit entry written
    entries = (
        db_session.query(AuditLog)
        .filter(AuditLog.action == expected_action)
        .all()
    )
    assert len(entries) == 1
    meta = json.loads(entries[0].extra_metadata)
    assert meta["batch_id"] == batch_id
    assert meta["integration"] == name


def test_trigger_unknown_integration_returns_400(
    client: TestClient, mixed_csv_bytes: bytes
) -> None:
    batch_id = _upload(client, mixed_csv_bytes)

    response = client.post(f"/api/batches/{batch_id}/integrations/zapier")

    assert response.status_code == 400
    assert "Unsupported" in response.json()["detail"]


def test_trigger_integration_with_unknown_batch_returns_404(
    client: TestClient,
) -> None:
    response = client.post(
        "/api/batches/no-such-batch/integrations/salesforce"
    )

    assert response.status_code == 404
