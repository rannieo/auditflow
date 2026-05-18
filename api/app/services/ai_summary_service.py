"""Generate a plain-English summary of a batch using aggregate metrics only.

The MVP is deterministic — no LLM API call. The intent is to demonstrate the
boundary and audit-log behavior. A real LLM provider can be swapped in here
later without changing the route or the audit contract.
"""

from collections import Counter

from sqlalchemy.orm import Session

from app.config import Settings, get_settings
from app.models.batch import Batch
from app.models.batch_record import BatchRecord
from app.services import audit_service


def generate_summary(
    db: Session, batch: Batch, *, settings: Settings | None = None
) -> str:
    provider = (settings or get_settings()).ai_provider
    summary = _build_summary_text(db, batch)
    audit_service.record_event(
        db,
        action="ai_summary_generated",
        metadata={
            "batch_id": batch.id,
            "passed": batch.passed_records,
            "failed": batch.failed_records,
            "duplicates": batch.duplicate_records,
            "provider": provider,
        },
    )
    return summary


def _build_summary_text(db: Session, batch: Batch) -> str:
    total = batch.total_records
    failed = batch.failed_records
    duplicates = batch.duplicate_records
    passed = batch.passed_records

    if total == 0:
        return "This batch contains no records."

    parts = [f"This batch contains {total} record(s)."]

    needs_review = failed + duplicates
    if needs_review == 0:
        parts.append("All records passed validation.")
        parts.append("Recommended action: this batch is safe to sync to downstream systems.")
        return " ".join(parts)

    reasons = _top_failure_reasons(db, batch.id)
    if reasons:
        reason_text = ", ".join(reasons)
        parts.append(
            f"{needs_review} record(s) require review due to {reason_text}."
        )
    else:
        parts.append(f"{needs_review} record(s) require review.")

    parts.append(
        f"Breakdown: {passed} passed, {failed} failed, {duplicates} duplicate."
    )
    parts.append(
        "Recommended action: clean failed records before syncing to downstream systems."
    )
    return " ".join(parts)


def _top_failure_reasons(db: Session, batch_id: str, top_n: int = 3) -> list[str]:
    import json

    rows = (
        db.query(BatchRecord.validation_errors)
        .filter(BatchRecord.batch_id == batch_id)
        .filter(BatchRecord.validation_status != "passed")
        .all()
    )

    counter: Counter[str] = Counter()
    for (raw,) in rows:
        try:
            errors = json.loads(raw)
        except (ValueError, TypeError):
            continue
        if isinstance(errors, list):
            for err in errors:
                counter[_friendly(str(err))] += 1

    return [reason for reason, _ in counter.most_common(top_n)]


def _friendly(error: str) -> str:
    """Map raw validation errors to short, human-readable phrases."""
    mapping = {
        "client_name is required": "missing client name",
        "email is required": "missing email",
        "email is not a valid email address": "invalid email",
        "amount is required": "missing amount",
        "amount must be a number": "invalid amount",
        "amount must be greater than 0": "invalid amount",
        "service_type is required": "missing service type",
        "status is required": "missing status",
        "date is required": "missing date",
        "date must be a valid ISO date (YYYY-MM-DD)": "invalid date",
        "duplicate record": "duplicate entry",
    }
    for key, label in mapping.items():
        if error.startswith(key):
            return label
    if error.startswith("service_type must be one of"):
        return "invalid service type"
    if error.startswith("status must be one of"):
        return "invalid status"
    return error
