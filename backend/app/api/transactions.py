from datetime import datetime, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import case, func, select
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.db.session import get_db
from app.models.account import Account
from app.models.category import Category
from app.models.transaction import Transaction, TransactionType
from app.models.transaction_audit import TransactionAudit
from app.models.user import User
from app.schemas.finance import (TransactionCreate, TransactionResponse, TransactionUpdate, TransactionReverse, TransactionAuditResponse)

router = APIRouter(prefix="/transactions", tags=["transactions"])

def _snapshot(transaction: Transaction) -> dict:
    return {
        "id": str(transaction.id),
        "user_id": str(transaction.user_id),
        "account_id": str(transaction.account_id),
        "category_id": str(transaction.category_id) if transaction.category_id else None,
        "transaction_type": transaction.transaction_type.value,
        "amount_paise": transaction.amount_paise,
        "currency": transaction.currency,
        "description": transaction.description,
        "notes": transaction.notes,
        "occurred_at": transaction.occurred_at.isoformat() if transaction.occurred_at else None,
        "is_reversed": transaction.is_reversed,
        "reversal_of_id": str(transaction.reversal_of_id) if transaction.reversal_of_id else None,
    }


def _audit(db: Session, user_id: UUID, transaction_id: UUID, event_type: str,
           reason: str | None, before: dict | None, after: dict | None) -> None:
    db.add(TransactionAudit(
        user_id=user_id, transaction_id=transaction_id, event_type=event_type,
        reason=reason, before_snapshot=before, after_snapshot=after,
    ))



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
            Category.kind == payload.transaction_type, Category.is_active.is_(True),
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
    db.flush()
    _audit(db, current_user.id, transaction.id, "created", None, None, _snapshot(transaction))
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


@router.get("/summary", response_model=dict[str, int | str])
def transaction_summary(
    currency: str = Query(default="INR", min_length=3, max_length=3),
    start_at: datetime | None = None,
    end_at: datetime | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict[str, int | str]:
    query = select(
        func.coalesce(func.sum(case(
            (Transaction.transaction_type == TransactionType.INCOME, Transaction.amount_paise),
            else_=0,
        )), 0).label("income"),
        func.coalesce(func.sum(case(
            (Transaction.transaction_type == TransactionType.EXPENSE, Transaction.amount_paise),
            else_=0,
        )), 0).label("expense"),
    ).where(Transaction.user_id == current_user.id, Transaction.currency == currency.upper())
    if start_at is not None:
        query = query.where(Transaction.occurred_at >= start_at)
    if end_at is not None:
        query = query.where(Transaction.occurred_at <= end_at)

    row = db.execute(query).one()
    income_paise, expense_paise = int(row.income), int(row.expense)
    return {
        "currency": currency.upper(),
        "income_paise": income_paise,
        "expense_paise": expense_paise,
        "net_cash_flow_paise": income_paise - expense_paise,
    }


@router.get("/{transaction_id}", response_model=TransactionResponse)
def get_transaction(transaction_id: UUID, db: Session = Depends(get_db),
                    current_user: User = Depends(get_current_user)) -> Transaction:
    transaction = db.scalar(select(Transaction).where(
        Transaction.id == transaction_id, Transaction.user_id == current_user.id
    ))
    if transaction is None:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return transaction

@router.patch("/{transaction_id}", response_model=TransactionResponse)
def update_transaction(
    transaction_id: UUID, payload: TransactionUpdate,
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user),
) -> Transaction:
    transaction = db.scalar(select(Transaction).where(
        Transaction.id == transaction_id, Transaction.user_id == current_user.id,
    ).with_for_update())
    if transaction is None:
        raise HTTPException(status_code=404, detail="Transaction not found")
    if transaction.is_reversed or transaction.reversal_of_id is not None:
        raise HTTPException(status_code=409, detail="Reversed transactions cannot be edited")

    changes = payload.model_dump(exclude_unset=True)
    if not changes:
        return transaction
    if "category_id" in changes and changes["category_id"] is not None:
        category = db.scalar(select(Category).where(
            Category.id == changes["category_id"], Category.user_id == current_user.id,
            Category.kind == transaction.transaction_type, Category.is_active.is_(True),
        ))
        if category is None:
            raise HTTPException(status_code=404, detail="Active category not found for transaction type")

    before = _snapshot(transaction)
    for key, value in changes.items():
        if key == "description" and value is not None:
            value = value.strip()
            if not value:
                raise HTTPException(status_code=422, detail="Description cannot be blank")
        setattr(transaction, key, value)
    _audit(db, current_user.id, transaction.id, "updated", None, before, _snapshot(transaction))
    db.commit()
    db.refresh(transaction)
    return transaction


@router.post("/{transaction_id}/reverse", response_model=TransactionResponse, status_code=status.HTTP_201_CREATED)
def reverse_transaction(
    transaction_id: UUID, payload: TransactionReverse,
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user),
) -> Transaction:
    original = db.scalar(select(Transaction).where(
        Transaction.id == transaction_id, Transaction.user_id == current_user.id,
    ).with_for_update())
    if original is None:
        raise HTTPException(status_code=404, detail="Transaction not found")
    if original.is_reversed:
        raise HTTPException(status_code=409, detail="Transaction has already been reversed")
    if original.reversal_of_id is not None:
        raise HTTPException(status_code=409, detail="A reversal transaction cannot itself be reversed")

    before = _snapshot(original)
    original.is_reversed = True
    reversal_type = TransactionType.EXPENSE if original.transaction_type == TransactionType.INCOME else TransactionType.INCOME
    reversal = Transaction(
        user_id=current_user.id, account_id=original.account_id, category_id=original.category_id,
        transaction_type=reversal_type, amount_paise=original.amount_paise,
        currency=original.currency, description=f"Reversal: {original.description}"[:240],
        notes=f"Reversal of transaction {original.id}. Reason: {payload.reason.strip()}",
        occurred_at=datetime.now(timezone.utc), reversal_of_id=original.id,
    )
    db.add(reversal)
    db.flush()
    _audit(db, current_user.id, original.id, "reversed", payload.reason.strip(), before, _snapshot(original))
    _audit(db, current_user.id, reversal.id, "reversal_created", payload.reason.strip(), None, _snapshot(reversal))
    db.commit()
    db.refresh(reversal)
    return reversal


@router.get("/{transaction_id}/audit", response_model=list[TransactionAuditResponse])
def transaction_audit_history(
    transaction_id: UUID, db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[TransactionAudit]:
    exists = db.scalar(select(Transaction.id).where(
        Transaction.id == transaction_id, Transaction.user_id == current_user.id,
    ))
    if exists is None:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return list(db.scalars(select(TransactionAudit).where(
        TransactionAudit.transaction_id == transaction_id, TransactionAudit.user_id == current_user.id,
    ).order_by(TransactionAudit.created_at.asc())).all())

