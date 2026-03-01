from fastapi import APIRouter
from app.schemas import HealthCheck, DetailedHealthCheck

router = APIRouter()

@router.get("/health", response_model=HealthCheck)
async def health():
    return HealthCheck(status="ok")

@router.get("/api/v1/health", response_model=DetailedHealthCheck)
async def detailed_health():
    return DetailedHealthCheck(
        status="ok",
        components={
            "api": "healthy",
            "services": "healthy"
        }
    )
