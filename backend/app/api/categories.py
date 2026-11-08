from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.db.session import get_db
from app.models.category import Category
from app.models.user import User
from app.schemas.category import CategoryCreate, CategoryResponse, CategoryUpdate

router = APIRouter(prefix="/categories", tags=["categories"])


@router.get("", response_model=list[CategoryResponse])
def list_categories(db: Session = Depends(get_db),
                    current_user: User = Depends(get_current_user)) -> list[Category]:
    return list(db.scalars(select(Category).where(
        Category.user_id == current_user.id, Category.is_active.is_(True)
    ).order_by(Category.kind, Category.name)).all())


@router.post("", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
def create_category(payload: CategoryCreate, db: Session = Depends(get_db),
                    current_user: User = Depends(get_current_user)) -> Category:
    name = payload.name.strip()
    if not name:
        raise HTTPException(status_code=422, detail="Category name cannot be blank")
    existing = db.scalar(select(Category).where(
        Category.user_id == current_user.id, Category.kind == payload.kind,
        Category.name.ilike(name),
    ))
    if existing:
        raise HTTPException(status_code=409, detail="Category already exists")
    category = Category(user_id=current_user.id, name=name, kind=payload.kind, is_default=False)
    db.add(category)
    db.commit()
    db.refresh(category)
    return category



@router.patch("/{category_id}", response_model=CategoryResponse)
def update_category(
    category_id: UUID,
    payload: CategoryUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Category:
    category = db.scalar(select(Category).where(
        Category.id == category_id,
        Category.user_id == current_user.id,
    ))
    if category is None:
        raise HTTPException(status_code=404, detail="Category not found")

    changes = payload.model_dump(exclude_unset=True)
    if "name" in changes:
        name = changes["name"].strip()
        if not name:
            raise HTTPException(status_code=422, detail="Category name cannot be blank")
        duplicate = db.scalar(select(Category).where(
            Category.user_id == current_user.id,
            Category.kind == category.kind,
            Category.id != category.id,
            Category.name.ilike(name),
        ))
        if duplicate is not None:
            raise HTTPException(status_code=409, detail="Category already exists")
        category.name = name

    if "is_active" in changes and changes["is_active"] is not None:
        category.is_active = changes["is_active"]

    db.commit()
    db.refresh(category)
    return category
