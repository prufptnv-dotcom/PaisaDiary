from datetime import datetime, timezone
from enum import Enum
from uuid import UUID, uuid4

from sqlalchemy import BigInteger, CheckConstraint, DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class AccountType(str, Enum):
    CASH = "cash"
    BANK = "bank"
    UPI = "upi"
    WALLET = "wallet"
    OTHER = "other"


class Account(Base):
    __tablename__ = "accounts"
    __table_args__ = (
        CheckConstraint("opening_balance_paise >= 0", name="ck_accounts_opening_balance_nonnegative"),
    )

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    name: Mapped[str] = mapped_column(String(100))
    account_type: Mapped[AccountType]
    currency: Mapped[str] = mapped_column(String(3), default="INR")
    opening_balance_paise: Mapped[int] = mapped_column(BigInteger, default=0)
    is_active: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
