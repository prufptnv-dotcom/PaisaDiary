from datetime import datetime, timezone
from uuid import UUID, uuid4

from sqlalchemy import DateTime, ForeignKey, JSON, String, Text, Index
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class TransactionAudit(Base):
    __tablename__ = "transaction_audits"
    __table_args__ = (
        Index("ix_transaction_audits_user_created", "user_id", "created_at"),
        Index("ix_transaction_audits_transaction_created", "transaction_id", "created_at"),
    )

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    transaction_id: Mapped[UUID] = mapped_column(
        ForeignKey("transactions.id", ondelete="RESTRICT"), index=True
    )
    event_type: Mapped[str] = mapped_column(String(24))
    reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    before_snapshot: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    after_snapshot: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
