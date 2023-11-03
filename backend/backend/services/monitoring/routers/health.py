from typing import Annotated

from fastapi import APIRouter, Depends, Response, status
from fastapi.concurrency import run_in_threadpool
from sqlalchemy import text

from backend.config.settings import settings
from backend.db import get_db
from backend.libs.db.session import AsyncSession
from backend.services.monitoring.exceptions import HealthError
from backend.services.monitoring.operations.health import HealthCheck, check_health
from backend.services.monitoring.tasks import check_health_task

_monitoring_settings = settings.monitoring

router = APIRouter()


async def get_health_checks(
    db: Annotated[AsyncSession, Depends(get_db)]
) -> list[HealthCheck]:
    async def check_database() -> None:
        await db.execute(text("SELECT 1"))

    async def check_worker() -> None:
        result = check_health_task.delay()
        timeout = _monitoring_settings.worker_health_check_timeout.total_seconds()

        def check_result() -> None:
            if result.get(timeout=timeout) is not True:
                msg = "Invalid worker's task result"
                raise AssertionError(msg)

        await run_in_threadpool(check_result)

    return [
        HealthCheck(name="database", check=check_database),
        HealthCheck(name="worker", check=check_worker),
    ]


@router.get(
    "",
    responses={
        200: {
            "description": "Healthy",
            "headers": {"Content-Type": "application/json"},
            "content": {
                "application/json": {
                    "example": {
                        "database": "OK",
                        "worker": "OK",
                    },
                }
            },
        },
        503: {
            "description": "Unhealthy",
            "headers": {"Content-Type": "application/json"},
            "content": {
                "application/json": {
                    "example": {
                        "database": "Failed",
                        "worker": "OK",
                    },
                }
            },
        },
    },
)
async def check_health_route(
    checks: Annotated[list[HealthCheck], Depends(get_health_checks)], response: Response
) -> dict[str, str]:
    try:
        return await check_health(checks)
    except HealthError as exc:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        return exc.report
