from datetime import datetime, timezone
from enum import Enum
from uuid import UUID, uuid4

from sqlalchemy import BigInteger, CheckConstraint, DateTime, ForeignKey, Index, String, Text, Boolean
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class TransactionType(str, Enum):
    EXPENSE = "expense"
    INCOME = "income"


class Transaction(Base):
    __tablename__ = "transactions"
    __table_args__ = (
        CheckConstraint("amount_paise > 0", name="ck_transactions_amount_positive"),
        Index("ix_transactions_user_occurred", "user_id", "occurred_at"),
    )

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    account_id: Mapped[UUID] = mapped_column(ForeignKey("accounts.id", ondelete="RESTRICT"), index=True)
    category_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("categories.id", ondelete="SET NULL"), nullable=True, index=True
    )
    transaction_type: Mapped[TransactionType]
    amount_paise: Mapped[int] = mapped_column(BigInteger)
    currency: Mapped[str] = mapped_column(String(3), default="INR")
    description: Mapped[str] = mapped_column(String(240))
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    occurred_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True
    )
    is_reversed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    reversal_of_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("transactions.id", ondelete="RESTRICT"), nullable=True, unique=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
