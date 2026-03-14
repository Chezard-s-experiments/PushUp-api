from fastapi import APIRouter

router = APIRouter(tags=["Health"])


@router.get("/health", operation_id="HealthCheck")
async def health_check() -> dict[str, str]:
    return {"status": "ok"}
