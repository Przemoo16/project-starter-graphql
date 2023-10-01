from fastapi import APIRouter

from backend.services.monitoring.routers.router import router as monitoring_router

_router = APIRouter()
_router.include_router(monitoring_router, prefix="/monitoring", tags=["monitoring"])


def get_router() -> APIRouter:
    return _router
