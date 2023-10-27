from typing import Annotated

from fastapi import APIRouter, Depends, Response, status
from fastapi.concurrency import run_in_threadpool
from sqlalchemy import text

from backend.config.settings import get_settings
from backend.db import get_session
from backend.libs.db.session import AsyncSession
from backend.services.monitoring.exceptions import HealthError
from backend.services.monitoring.operations.health import HealthCheck, check_health
from backend.services.monitoring.tasks import check_health_task

monitoring_settings = get_settings().monitoring

router = APIRouter()


async def get_health_checks(
    session: Annotated[AsyncSession, Depends(get_session)]
) -> list[HealthCheck]:
    async def check_database() -> None:
        await session.execute(text("SELECT 1"))

    async def check_worker() -> None:
        result = check_health_task.delay()
        timeout = monitoring_settings.worker_health_check_timeout.total_seconds()

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
