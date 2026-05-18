from fastapi import APIRouter, HTTPException

from app.deps import DbSession
from app.models.batch import Batch
from app.schemas.batch_schema import IntegrationResponse
from app.services import integration_service
from app.services.integration_service import UnknownIntegrationError

router = APIRouter(prefix="/api/batches", tags=["integrations"])


@router.post(
    "/{batch_id}/integrations/{integration_name}",
    response_model=IntegrationResponse,
)
def trigger_integration(
    batch_id: str,
    integration_name: str,
    db: DbSession,
) -> IntegrationResponse:
    batch = db.get(Batch, batch_id)
    if batch is None:
        raise HTTPException(status_code=404, detail="Batch not found.")

    try:
        message = integration_service.trigger(
            db, batch=batch, integration=integration_name
        )
    except UnknownIntegrationError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return IntegrationResponse(status="success", message=message)
