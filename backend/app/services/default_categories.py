from sqlalchemy.orm import Session

from app.models.category import Category, CategoryKind

DEFAULT_EXPENSE_CATEGORIES = [
    "Food & Dining", "Groceries", "Transport", "Fuel", "Health", "Shopping",
    "Education", "Bills & Utilities", "Rent & Housing", "Entertainment",
    "Travel", "Personal Care", "Gifts & Donations", "Other",
]
DEFAULT_INCOME_CATEGORIES = [
    "Salary", "Scholarship", "Freelance", "Business", "Interest", "Gift", "Refund", "Other",
]


def seed_default_categories(db: Session, user_id) -> None:
    rows = [
        Category(user_id=user_id, name=name, kind=CategoryKind.EXPENSE, is_default=True)
        for name in DEFAULT_EXPENSE_CATEGORIES
    ] + [
        Category(user_id=user_id, name=name, kind=CategoryKind.INCOME, is_default=True)
        for name in DEFAULT_INCOME_CATEGORIES
    ]
    db.add_all(rows)
