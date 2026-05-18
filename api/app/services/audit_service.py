"""Write and read audit log entries."""

import json
from typing import Any

from sqlalchemy import desc
from sqlalchemy.orm import Session

from app.models.audit_log import AuditLog
from app.schemas.audit_schema import AuditLogOut

DEFAULT_ACTOR = "demo-user"


def record_event(
    db: Session,
    *,
    action: str,
    metadata: dict[str, Any] | None = None,
    actor: str = DEFAULT_ACTOR,
    status: str = "success",
) -> AuditLog:
    entry = AuditLog(
        action=action,
        actor=actor,
        status=status,
        extra_metadata=json.dumps(metadata or {}),
    )
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry


def list_recent(db: Session, *, limit: int = 100) -> list[AuditLogOut]:
    rows = (
        db.query(AuditLog)
        .order_by(desc(AuditLog.created_at), desc(AuditLog.id))
        .limit(limit)
        .all()
    )
    return [
        AuditLogOut(
            id=row.id,
            action=row.action,
            actor=row.actor,
            status=row.status,
            metadata=_safe_json(row.extra_metadata),
            created_at=row.created_at,
        )
        for row in rows
    ]


def _safe_json(raw: str) -> dict[str, Any]:
    try:
        value = json.loads(raw)
        return value if isinstance(value, dict) else {}
    except (ValueError, TypeError):
        return {}
