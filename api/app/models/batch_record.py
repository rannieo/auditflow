from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


class BatchRecord(Base):
    __tablename__ = "batch_records"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    batch_id: Mapped[str] = mapped_column(
        String, ForeignKey("batches.id", ondelete="CASCADE"), nullable=False, index=True
    )

    client_name: Mapped[str | None] = mapped_column(String, nullable=True)
    email: Mapped[str | None] = mapped_column(String, nullable=True)
    amount: Mapped[float | None] = mapped_column(Numeric, nullable=True)
    service_type: Mapped[str | None] = mapped_column(String, nullable=True)
    status: Mapped[str | None] = mapped_column(String, nullable=True)
    date: Mapped[str | None] = mapped_column(String, nullable=True)

    # "passed" | "failed" | "duplicate"
    validation_status: Mapped[str] = mapped_column(String, nullable=False)
    # JSON-encoded list[str]
    validation_errors: Mapped[str] = mapped_column(Text, nullable=False, default="[]")

    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow
    )

    batch: Mapped["Batch"] = relationship(back_populates="records")  # noqa: F821
