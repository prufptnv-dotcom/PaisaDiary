from fastapi import FastAPI

from app.api.accounts import router as accounts_router
from app.api.auth import router as auth_router
from app.api.categories import router as categories_router
from app.api.health import router as health_router
from app.api.transactions import router as transactions_router
from app.core.config import get_settings

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Personal finance API for PaisaDiary.",
)

app.include_router(health_router, prefix=settings.api_v1_prefix)
app.include_router(auth_router, prefix=settings.api_v1_prefix)
app.include_router(accounts_router, prefix=settings.api_v1_prefix)
app.include_router(categories_router, prefix=settings.api_v1_prefix)
app.include_router(transactions_router, prefix=settings.api_v1_prefix)


@app.get("/", tags=["root"])
def root() -> dict[str, str]:
    return {"app": settings.app_name, "status": "running"}
