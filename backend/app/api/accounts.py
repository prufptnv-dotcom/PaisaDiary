from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.db.session import get_db
from app.models.account import Account
from app.models.user import User
from app.schemas.finance import AccountCreate, AccountResponse, AccountUpdate
from app.services.balances import get_account_balance_paise

router = APIRouter(prefix="/accounts", tags=["accounts"])


@router.post("", response_model=AccountResponse, status_code=status.HTTP_201_CREATED)
def create_account(payload: AccountCreate, db: Session = Depends(get_db),
                   current_user: User = Depends(get_current_user)) -> Account:
    account = Account(
        user_id=current_user.id,
        name=payload.name.strip(),
        account_type=payload.account_type,
        opening_balance_paise=payload.opening_balance_paise,
        currency=payload.currency.upper(),
    )
    db.add(account)
    db.commit()
    db.refresh(account)
    return account


@router.get("", response_model=list[AccountResponse])
def list_accounts(db: Session = Depends(get_db),
                  current_user: User = Depends(get_current_user)) -> list[Account]:
    return list(db.scalars(select(Account).where(Account.user_id == current_user.id)
                            .order_by(Account.created_at.desc())).all())


@router.get("/{account_id}", response_model=AccountResponse)
def get_account(account_id: UUID, db: Session = Depends(get_db),
                current_user: User = Depends(get_current_user)) -> Account:
    account = db.scalar(select(Account).where(Account.id == account_id,
                                              Account.user_id == current_user.id))
    if account is None:
        raise HTTPException(status_code=404, detail="Account not found")
    return account


@router.patch("/{account_id}", response_model=AccountResponse)
def update_account(account_id: UUID, payload: AccountUpdate, db: Session = Depends(get_db),
                   current_user: User = Depends(get_current_user)) -> Account:
    account = db.scalar(select(Account).where(Account.id == account_id,
                                              Account.user_id == current_user.id))
    if account is None:
        raise HTTPException(status_code=404, detail="Account not found")
    for key, value in payload.model_dump(exclude_unset=True).items():
        if value is not None:
            setattr(account, key, value.strip() if key == "name" else value)
    db.commit()
    db.refresh(account)
    return account


@router.get("/{account_id}/balance", response_model=dict[str, int])
def account_balance(account_id: UUID, db: Session = Depends(get_db),
                    current_user: User = Depends(get_current_user)) -> dict[str, int]:
    try:
        balance = get_account_balance_paise(db, user_id=current_user.id, account_id=account_id)
    except ValueError:
        raise HTTPException(status_code=404, detail="Account not found")
    return {"balance_paise": balance}
