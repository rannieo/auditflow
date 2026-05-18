from datetime import datetime
from typing import Any

from pydantic import BaseModel


class AuditLogOut(BaseModel):
    id: int
    action: str
    actor: str
    status: str
    metadata: dict[str, Any]
    created_at: datetime
