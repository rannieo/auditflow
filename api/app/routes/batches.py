from typing import Annotated

from fastapi import APIRouter, File, HTTPException, UploadFile, status

from app.deps import DbSession
from app.schemas.batch_schema import BatchDetail, BatchSummary
from app.services import batch_service
from app.services.csv_parser import CsvParseError, parse_csv
from app.services.validation_service import validate_rows

router = APIRouter(prefix="/api/batches", tags=["batches"])


@router.post("/upload", response_model=BatchSummary, status_code=status.HTTP_201_CREATED)
async def upload_batch(
    db: DbSession,
    file: Annotated[UploadFile, File(description="CSV of client service records")],
) -> BatchSummary:
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file uploaded.")
    if not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="File must be a .csv file.")

    raw = await file.read()
    if not raw:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    try:
        rows = parse_csv(raw)
    except CsvParseError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    records = validate_rows(rows)
    return batch_service.create_batch(db, filename=file.filename, records=records)


@router.get("/{batch_id}", response_model=BatchDetail)
def get_batch(batch_id: str, db: DbSession) -> BatchDetail:
    detail = batch_service.get_batch_detail(db, batch_id)
    if detail is None:
        raise HTTPException(status_code=404, detail="Batch not found.")
    return detail
