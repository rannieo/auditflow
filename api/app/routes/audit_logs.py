from typing import Annotated

from fastapi import APIRouter, Query

from app.deps import DbSession
from app.schemas.audit_schema import AuditLogOut
from app.services import audit_service

router = APIRouter(prefix="/api/audit-logs", tags=["audit-logs"])


@router.get("", response_model=list[AuditLogOut])
def list_audit_logs(
    db: DbSession,
    limit: Annotated[int, Query(ge=1, le=500)] = 100,
) -> list[AuditLogOut]:
    return audit_service.list_recent(db, limit=limit)
