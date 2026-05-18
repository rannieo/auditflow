"""Generate a plain-English summary of a batch using aggregate metrics only.

Provider selection happens in ``ai_providers.factory.get_provider``. This
module is responsible for building ``BatchMetrics`` (which never carries
raw record values), dispatching to the provider, and writing the audit
log — including the degraded-fallback path.
"""

import json
import time
from collections import Counter

from sqlalchemy.orm import Session

from app.models.batch import Batch
from app.models.batch_record import BatchRecord
from app.services import audit_service
from app.services.ai_providers import AiProvider, BatchMetrics
from app.services.ai_providers.mock_provider import MockProvider


def generate_summary(
    db: Session,
    batch: Batch,
    *,
    provider: AiProvider,
) -> str:
    metrics = _build_metrics(db, batch)
    started = time.perf_counter()

    base_meta: dict[str, object] = {
        "batch_id": batch.id,
        "passed": batch.passed_records,
        "failed": batch.failed_records,
        "duplicates": batch.duplicate_records,
    }

    try:
        text = provider.summarize(metrics)
    except Exception as exc:  # noqa: BLE001 — any provider failure → fallback
        fallback_text = MockProvider().summarize(metrics)
        audit_service.record_event(
            db,
            action="ai_summary_generated",
            status="degraded",
            metadata={
                **base_meta,
                "provider": "mock",
                "fallback_from": provider.name,
                "provider_error": _truncate(repr(exc), 200),
            },
        )
        return fallback_text

    latency_ms = int((time.perf_counter() - started) * 1000)
    meta: dict[str, object] = {
        **base_meta,
        "provider": provider.name,
        "latency_ms": latency_ms,
    }
    model = getattr(provider, "model", None)
    if model:
        meta["model"] = model

    audit_service.record_event(
        db, action="ai_summary_generated", metadata=meta
    )
    return text


def _build_metrics(db: Session, batch: Batch) -> BatchMetrics:
    return BatchMetrics(
        filename=batch.filename,
        total=batch.total_records,
        passed=batch.passed_records,
        failed=batch.failed_records,
        duplicate=batch.duplicate_records,
        top_reasons=_top_failure_reasons(db, batch.id),
    )


def _top_failure_reasons(db: Session, batch_id: str, top_n: int = 3) -> list[str]:
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


def _truncate(text: str, limit: int) -> str:
    return text if len(text) <= limit else text[: limit - 1] + "…"
