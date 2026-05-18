from fastapi import APIRouter, HTTPException

from app.deps import DbSession, SettingsDep
from app.models.batch import Batch
from app.schemas.batch_schema import AiSummaryResponse
from app.services import ai_summary_service

router = APIRouter(prefix="/api/batches", tags=["ai"])


@router.post("/{batch_id}/ai-summary", response_model=AiSummaryResponse)
def ai_summary(
    batch_id: str,
    db: DbSession,
    settings: SettingsDep,
) -> AiSummaryResponse:
    batch = db.get(Batch, batch_id)
    if batch is None:
        raise HTTPException(status_code=404, detail="Batch not found.")
    summary = ai_summary_service.generate_summary(db, batch, settings=settings)
    return AiSummaryResponse(summary=summary)
