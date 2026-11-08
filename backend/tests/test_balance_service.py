from uuid import uuid4
import pytest

from app.services.balances import get_account_balance_paise


class FakeScalarResult:
    def __init__(self, value):
        self.value = value
    def __call__(self):
        return self.value


def test_balance_service_requires_account_for_user():
    class FakeDB:
        def scalar(self, query):
            return None
    with pytest.raises(ValueError, match="Account not found"):
        get_account_balance_paise(FakeDB(), user_id=uuid4(), account_id=uuid4())
