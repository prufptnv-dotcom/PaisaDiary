from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.models.account import AccountType
from app.models.transaction import TransactionType


class AccountCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    account_type: AccountType
    opening_balance_paise: int = Field(default=0, ge=0)
    currency: str = Field(default="INR", min_length=3, max_length=3)


class AccountUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=100)
    is_active: bool | None = None


class AccountResponse(BaseModel):
    id: UUID
    name: str
    account_type: AccountType
    currency: str
    opening_balance_paise: int
    is_active: bool

    model_config = ConfigDict(from_attributes=True)


class TransactionCreate(BaseModel):
    account_id: UUID
    category_id: UUID | None = None
    transaction_type: TransactionType
    amount_paise: int = Field(gt=0)
    currency: str = Field(default="INR", min_length=3, max_length=3)
    description: str = Field(min_length=1, max_length=240)
    notes: str | None = None
    occurred_at: datetime | None = None


class TransactionResponse(BaseModel):
    id: UUID
    account_id: UUID
    category_id: UUID | None
    transaction_type: TransactionType
    amount_paise: int
    currency: str
    description: str
    notes: str | None
    occurred_at: datetime
    is_reversed: bool
    reversal_of_id: UUID | None

    model_config = ConfigDict(from_attributes=True)



class TransactionUpdate(BaseModel):
    category_id: UUID | None = None
    amount_paise: int | None = Field(default=None, gt=0)
    description: str | None = Field(default=None, min_length=1, max_length=240)
    notes: str | None = None
    occurred_at: datetime | None = None


class TransactionReverse(BaseModel):
    reason: str = Field(min_length=3, max_length=500)


class TransactionAuditResponse(BaseModel):
    id: UUID
    transaction_id: UUID
    event_type: str
    reason: str | None
    before_snapshot: dict | None
    after_snapshot: dict | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
