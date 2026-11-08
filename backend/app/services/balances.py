from uuid import UUID

from sqlalchemy import case, func, select
from sqlalchemy.orm import Session

from app.models.account import Account
from app.models.transaction import Transaction, TransactionType


def get_account_balance_paise(db: Session, *, user_id: UUID, account_id: UUID) -> int:
    """Return account balance in paise using persisted transactions.

    Expense amounts are stored as positive magnitudes and deducted; income amounts
    are stored as positive magnitudes and added. User ownership is part of the query.
    """
    account = db.scalar(
        select(Account).where(Account.id == account_id, Account.user_id == user_id)
    )
    if account is None:
        raise ValueError("Account not found")

    net_transactions = db.scalar(
        select(
            func.coalesce(
                func.sum(
                    case(
                        (Transaction.transaction_type == TransactionType.INCOME,
                         Transaction.amount_paise),
                        else_=-Transaction.amount_paise,
                    )
                ),
                0,
            )
        ).where(
            Transaction.account_id == account_id,
            Transaction.user_id == user_id,
            Transaction.currency == account.currency,
        )
    )
    return account.opening_balance_paise + int(net_transactions or 0)
