"""Integration tests for GET /api/audit-logs."""

from fastapi.testclient import TestClient


def _upload(client: TestClient, content: bytes) -> str:
    return client.post(
        "/api/batches/upload",
        files={"file": ("sample.csv", content, "text/csv")},
    ).json()["batch_id"]


def test_list_audit_logs_on_empty_db_returns_empty_list(
    client: TestClient,
) -> None:
    response = client.get("/api/audit-logs")

    assert response.status_code == 200
    assert response.json() == []


def test_list_audit_logs_returns_entries_newest_first(
    client: TestClient, mixed_csv_bytes: bytes
) -> None:
    batch_id = _upload(client, mixed_csv_bytes)
    client.post(f"/api/batches/{batch_id}/ai-summary")
    client.post(f"/api/batches/{batch_id}/integrations/salesforce")

    response = client.get("/api/audit-logs")

    assert response.status_code == 200
    logs = response.json()
    actions = [log["action"] for log in logs]
    # Newest first: integration -> ai_summary -> batch_validated -> csv_uploaded
    assert actions[0] == "integration_salesforce_triggered"
    assert actions[-1] == "csv_uploaded"
    assert {"csv_uploaded", "batch_validated", "ai_summary_generated"}.issubset(
        set(actions)
    )


def test_list_audit_logs_respects_limit_query_param(
    client: TestClient, mixed_csv_bytes: bytes
) -> None:
    _upload(client, mixed_csv_bytes)  # writes 2 audit entries

    response = client.get("/api/audit-logs?limit=1")

    assert response.status_code == 200
    assert len(response.json()) == 1


def test_list_audit_logs_rejects_invalid_limit(client: TestClient) -> None:
    response = client.get("/api/audit-logs?limit=0")

    assert response.status_code == 422
