from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class BatchSummary(BaseModel):
    """Returned by POST /api/batches/upload and embedded in batch details."""

    batch_id: str
    filename: str
    total_records: int
    passed_records: int
    failed_records: int
    duplicate_records: int
    created_at: datetime


class BatchRecordOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    client_name: str | None
    email: str | None
    amount: float | None
    service_type: str | None
    status: str | None
    date: str | None
    validation_status: str
    validation_errors: list[str] = Field(default_factory=list)


class BatchDetail(BaseModel):
    summary: BatchSummary
    records: list[BatchRecordOut]


class AiSummaryResponse(BaseModel):
    summary: str


class IntegrationResponse(BaseModel):
    status: str
    message: str
