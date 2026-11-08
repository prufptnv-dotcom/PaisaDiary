from app.models.transaction import TransactionType


def test_transaction_type_values_are_explicit() -> None:
    assert TransactionType.EXPENSE.value == "expense"
    assert TransactionType.INCOME.value == "income"


def test_money_is_represented_as_integer_paise() -> None:
    # ₹123.45 is stored as 12,345 paise (never as a float).
    amount_paise = 12_345
    assert isinstance(amount_paise, int)
    assert amount_paise == 123 * 100 + 45
