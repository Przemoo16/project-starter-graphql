from typing import Annotated

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from backend.db import get_session
from backend.services.monitoring.exceptions import HealthError
from backend.services.monitoring.operations.health import HealthCheck, check_health
from backend.services.monitoring.tasks import check_health_task

router = APIRouter()


def get_health_checks(
    session: Annotated[AsyncSession, Depends(get_session)]
) -> list[HealthCheck]:
    async def check_database() -> None:
        await session.execute(text("SELECT 1"))

    async def check_worker() -> None:
        result = check_health_task.delay()
        if result.get() is not True:
            msg = "Invalid worker's task result"
            raise AssertionError(msg)

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
