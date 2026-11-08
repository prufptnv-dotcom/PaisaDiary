from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.db.session import get_db
from app.models.account import Account
from app.models.category import Category
from app.models.transaction import Transaction, TransactionType
from app.models.user import User
from app.schemas.finance import TransactionCreate, TransactionResponse

router = APIRouter(prefix="/transactions", tags=["transactions"])


@router.post("", response_model=TransactionResponse, status_code=status.HTTP_201_CREATED)
def create_transaction(payload: TransactionCreate, db: Session = Depends(get_db),
                       current_user: User = Depends(get_current_user)) -> Transaction:
    account = db.scalar(select(Account).where(Account.id == payload.account_id,
                                              Account.user_id == current_user.id,
                                              Account.is_active.is_(True)))
    if account is None:
        raise HTTPException(status_code=404, detail="Active account not found")
    currency = payload.currency.upper()
    if currency != account.currency:
        raise HTTPException(status_code=422, detail="Transaction currency must match account currency")

    if payload.category_id is not None:
        category = db.scalar(select(Category).where(
            Category.id == payload.category_id, Category.user_id == current_user.id,
            Category.kind == payload.transaction_type,
        ))
        if category is None:
            raise HTTPException(status_code=404, detail="Category not found for this transaction type")

    transaction = Transaction(
        user_id=current_user.id,
        account_id=account.id,
        category_id=payload.category_id,
        transaction_type=payload.transaction_type,
        amount_paise=payload.amount_paise,
        currency=currency,
        description=payload.description.strip(),
        notes=payload.notes,
        occurred_at=payload.occurred_at or datetime.now().astimezone(),
    )
    db.add(transaction)
    db.commit()
    db.refresh(transaction)
    return transaction


@router.get("", response_model=list[TransactionResponse])
def list_transactions(
    account_id: UUID | None = None,
    transaction_type: TransactionType | None = None,
    start_at: datetime | None = None,
    end_at: datetime | None = None,
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[Transaction]:
    query = select(Transaction).where(Transaction.user_id == current_user.id)
    if account_id is not None:
        query = query.where(Transaction.account_id == account_id)
    if transaction_type is not None:
        query = query.where(Transaction.transaction_type == transaction_type)
    if start_at is not None:
        query = query.where(Transaction.occurred_at >= start_at)
    if end_at is not None:
        query = query.where(Transaction.occurred_at <= end_at)
    query = query.order_by(Transaction.occurred_at.desc()).limit(limit).offset(offset)
    return list(db.scalars(query).all())
