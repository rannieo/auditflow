"""Mock external integrations. No network calls — these return canned success
responses and record an audit log entry.

In production, each branch would call out to the real provider SDK and the
audit log would persist the remote ID returned by the upstream system.
"""

from sqlalchemy.orm import Session

from app.models.batch import Batch
from app.services import audit_service

ALLOWED_INTEGRATIONS = ("salesforce", "sharepoint", "monday")

_MESSAGES: dict[str, str] = {
    "salesforce": "Mock Salesforce sync completed.",
    "sharepoint": "Mock SharePoint export completed.",
    "monday": "Mock Monday.com task created.",
}

_ACTIONS: dict[str, str] = {
    "salesforce": "integration_salesforce_triggered",
    "sharepoint": "integration_sharepoint_triggered",
    "monday": "integration_monday_triggered",
}


class UnknownIntegrationError(ValueError):
    pass


def trigger(db: Session, *, batch: Batch, integration: str) -> str:
    name = integration.lower()
    if name not in ALLOWED_INTEGRATIONS:
        raise UnknownIntegrationError(
            f"Unsupported integration '{integration}'. "
            f"Allowed: {', '.join(ALLOWED_INTEGRATIONS)}."
        )

    audit_service.record_event(
        db,
        action=_ACTIONS[name],
        metadata={"batch_id": batch.id, "integration": name},
    )
    return _MESSAGES[name]
