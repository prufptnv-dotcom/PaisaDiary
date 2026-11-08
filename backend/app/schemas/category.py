from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.models.category import CategoryKind


class CategoryCreate(BaseModel):
    name: str = Field(min_length=1, max_length=80)
    kind: CategoryKind


class CategoryResponse(BaseModel):
    id: UUID
    name: str
    kind: CategoryKind
    is_default: bool
    is_active: bool

    model_config = ConfigDict(from_attributes=True)
