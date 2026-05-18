"""Validate parsed CSV rows against the AuditFlow business rules.

Each row is returned as a ``ValidatedRecord`` with a normalized representation
and a list of validation errors. Duplicate detection runs across the batch:
records sharing client_name + email + amount + service_type are flagged.
"""

import re
from collections import Counter
from dataclasses import dataclass, field
from datetime import date

ALLOWED_SERVICE_TYPES = frozenset(
    {"tax_filing", "audit_review", "bookkeeping", "advisory"}
)
ALLOWED_STATUSES = frozenset({"pending", "in_review", "approved", "rejected"})

_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

PASSED = "passed"
FAILED = "failed"
DUPLICATE = "duplicate"


@dataclass
class ValidatedRecord:
    client_name: str | None
    email: str | None
    amount: float | None
    service_type: str | None
    status: str | None
    date: str | None
    validation_status: str
    validation_errors: list[str] = field(default_factory=list)


def validate_rows(rows: list[dict[str, str]]) -> list[ValidatedRecord]:
    records = [_validate_row(row) for row in rows]
    _flag_duplicates(records)
    return records


def _validate_row(row: dict[str, str]) -> ValidatedRecord:
    errors: list[str] = []

    client_name = row.get("client_name") or None
    if not client_name:
        errors.append("client_name is required")

    email = row.get("email") or None
    if not email:
        errors.append("email is required")
    elif not _EMAIL_RE.match(email):
        errors.append("email is not a valid email address")

    amount_raw = row.get("amount") or ""
    amount: float | None
    try:
        amount = float(amount_raw) if amount_raw != "" else None
    except ValueError:
        amount = None
        errors.append("amount must be a number")
    if amount is None and "amount must be a number" not in errors:
        errors.append("amount is required")
    elif amount is not None and amount <= 0:
        errors.append("amount must be greater than 0")

    service_type = row.get("service_type") or None
    if not service_type:
        errors.append("service_type is required")
    elif service_type not in ALLOWED_SERVICE_TYPES:
        errors.append(
            f"service_type must be one of {sorted(ALLOWED_SERVICE_TYPES)}"
        )

    status = row.get("status") or None
    if not status:
        errors.append("status is required")
    elif status not in ALLOWED_STATUSES:
        errors.append(f"status must be one of {sorted(ALLOWED_STATUSES)}")

    date_raw = row.get("date") or None
    if not date_raw:
        errors.append("date is required")
    else:
        try:
            date.fromisoformat(date_raw)
        except ValueError:
            errors.append("date must be a valid ISO date (YYYY-MM-DD)")

    return ValidatedRecord(
        client_name=client_name,
        email=email,
        amount=amount,
        service_type=service_type,
        status=status,
        date=date_raw,
        validation_status=PASSED if not errors else FAILED,
        validation_errors=errors,
    )


def _flag_duplicates(records: list[ValidatedRecord]) -> None:
    keys = [
        (r.client_name, r.email, r.amount, r.service_type)
        for r in records
        if r.client_name and r.email and r.amount is not None and r.service_type
    ]
    counts = Counter(keys)
    for record in records:
        key = (record.client_name, record.email, record.amount, record.service_type)
        if counts.get(key, 0) > 1:
            record.validation_status = DUPLICATE
            if "duplicate record" not in record.validation_errors:
                record.validation_errors.append("duplicate record")
