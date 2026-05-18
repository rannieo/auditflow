"""Integration tests for /api/batches/*."""

from fastapi.testclient import TestClient


def _upload(client: TestClient, content: bytes, filename: str = "sample.csv"):
    return client.post(
        "/api/batches/upload",
        files={"file": (filename, content, "text/csv")},
    )


def test_upload_with_valid_csv_returns_summary(
    client: TestClient, mixed_csv_bytes: bytes
) -> None:
    response = _upload(client, mixed_csv_bytes)

    assert response.status_code == 201
    body = response.json()
    assert body["filename"] == "sample.csv"
    assert body["total_records"] == 4
    assert body["passed_records"] == 0
    assert body["failed_records"] == 2
    assert body["duplicate_records"] == 2
    assert body["batch_id"].startswith("batch_")


def test_upload_with_missing_file_part_returns_422(client: TestClient) -> None:
    # No "file" field at all — Starlette validates the multipart form and 422s.
    response = client.post("/api/batches/upload")

    assert response.status_code == 422


def test_upload_with_non_csv_extension_returns_400(client: TestClient) -> None:
    response = _upload(client, b"foo", filename="data.txt")

    assert response.status_code == 400
    assert "csv" in response.json()["detail"].lower()


def test_upload_with_empty_file_returns_400(client: TestClient) -> None:
    response = _upload(client, b"")

    assert response.status_code == 400
    assert "empty" in response.json()["detail"].lower()


def test_upload_with_missing_headers_returns_400(client: TestClient) -> None:
    bad = b"client_name,email\nAcme,a@b.co\n"

    response = _upload(client, bad)

    assert response.status_code == 400
    assert "header" in response.json()["detail"].lower()


def test_get_batch_returns_summary_and_records(
    client: TestClient, mixed_csv_bytes: bytes
) -> None:
    batch_id = _upload(client, mixed_csv_bytes).json()["batch_id"]

    response = client.get(f"/api/batches/{batch_id}")

    assert response.status_code == 200
    body = response.json()
    assert body["summary"]["batch_id"] == batch_id
    assert len(body["records"]) == 4


def test_get_batch_includes_validation_errors_per_record(
    client: TestClient, mixed_csv_bytes: bytes
) -> None:
    batch_id = _upload(client, mixed_csv_bytes).json()["batch_id"]

    body = client.get(f"/api/batches/{batch_id}").json()

    statuses = {r["validation_status"] for r in body["records"]}
    assert statuses == {"failed", "duplicate"}
    # XYZ LLC row has missing email
    xyz = next(r for r in body["records"] if r["client_name"] == "XYZ LLC")
    assert any("email" in err for err in xyz["validation_errors"])


def test_get_batch_with_unknown_id_returns_404(client: TestClient) -> None:
    response = client.get("/api/batches/does-not-exist")

    assert response.status_code == 404
