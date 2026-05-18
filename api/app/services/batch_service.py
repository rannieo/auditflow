"""Create batches, persist validated records, and read batch details."""

import json
import uuid
from collections.abc import Iterable

from sqlalchemy.orm import Session

from app.models.batch import Batch
from app.models.batch_record import BatchRecord
from app.schemas.batch_schema import (
    BatchDetail,
    BatchRecordOut,
    BatchSummary,
)
from app.services import audit_service
from app.services.validation_service import (
    DUPLICATE,
    FAILED,
    PASSED,
    ValidatedRecord,
)


def create_batch(
    db: Session,
    *,
    filename: str,
    records: list[ValidatedRecord],
) -> BatchSummary:
    counts = _count_statuses(records)

    batch = Batch(
        id=_new_batch_id(),
        filename=filename,
        total_records=len(records),
        passed_records=counts[PASSED],
        failed_records=counts[FAILED],
        duplicate_records=counts[DUPLICATE],
    )
    db.add(batch)
    db.flush()

    db.add_all(
        BatchRecord(
            batch_id=batch.id,
            client_name=r.client_name,
            email=r.email,
            amount=r.amount,
            service_type=r.service_type,
            status=r.status,
            date=r.date,
            validation_status=r.validation_status,
            validation_errors=json.dumps(r.validation_errors),
        )
        for r in records
    )

    audit_service.record_event(
        db,
        action="csv_uploaded",
        metadata={
            "batch_id": batch.id,
            "filename": filename,
            "total": batch.total_records,
        },
    )
    audit_service.record_event(
        db,
        action="batch_validated",
        metadata={
            "batch_id": batch.id,
            "passed": batch.passed_records,
            "failed": batch.failed_records,
            "duplicates": batch.duplicate_records,
        },
    )

    db.commit()
    db.refresh(batch)
    return _to_summary(batch)


def get_batch_detail(db: Session, batch_id: str) -> BatchDetail | None:
    batch = db.get(Batch, batch_id)
    if batch is None:
        return None

    records = [
        BatchRecordOut(
            id=r.id,
            client_name=r.client_name,
            email=r.email,
            amount=float(r.amount) if r.amount is not None else None,
            service_type=r.service_type,
            status=r.status,
            date=r.date,
            validation_status=r.validation_status,
            validation_errors=_safe_json_list(r.validation_errors),
        )
        for r in batch.records
    ]
    return BatchDetail(summary=_to_summary(batch), records=records)


def get_batch_summary(db: Session, batch_id: str) -> BatchSummary | None:
    batch = db.get(Batch, batch_id)
    return _to_summary(batch) if batch else None


def _count_statuses(records: Iterable[ValidatedRecord]) -> dict[str, int]:
    counts = {PASSED: 0, FAILED: 0, DUPLICATE: 0}
    for r in records:
        counts[r.validation_status] = counts.get(r.validation_status, 0) + 1
    return counts


def _to_summary(batch: Batch) -> BatchSummary:
    return BatchSummary(
        batch_id=batch.id,
        filename=batch.filename,
        total_records=batch.total_records,
        passed_records=batch.passed_records,
        failed_records=batch.failed_records,
        duplicate_records=batch.duplicate_records,
        created_at=batch.created_at,
    )


def _new_batch_id() -> str:
    return f"batch_{uuid.uuid4().hex[:8]}"


def _safe_json_list(raw: str) -> list[str]:
    try:
        value = json.loads(raw)
        return [str(v) for v in value] if isinstance(value, list) else []
    except (ValueError, TypeError):
        return []
