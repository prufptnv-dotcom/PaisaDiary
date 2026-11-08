from fastapi import APIRouter

router = APIRouter(tags=["health"])


@router.get("/health", summary="Liveness check")
def health() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/ready", summary="Readiness check")
def readiness() -> dict[str, str]:
    # Database connectivity is added with the first persistence increment.
    return {"status": "ready"}
