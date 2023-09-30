from fastapi import APIRouter

from backend.services.monitoring.routers.health import router as health_router

router = APIRouter()
router.include_router(health_router, prefix="/health")
