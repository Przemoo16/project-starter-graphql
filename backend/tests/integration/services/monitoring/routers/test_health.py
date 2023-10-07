import pytest
from fastapi import FastAPI, status
from httpx import AsyncClient

from backend.services.monitoring.operations.health import HealthCheck
from backend.services.monitoring.routers.health import get_health_checks


@pytest.mark.anyio()
async def test_check_health_healthy(async_client: AsyncClient) -> None:
    response = await async_client.get("/rest/monitoring/health")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "database": "OK",
        "worker": "OK",
    }


@pytest.mark.anyio()
async def test_check_health_unhealthy(app: FastAPI, async_client: AsyncClient) -> None:
    async def success_check() -> None:
        pass

    async def failed_check() -> None:
        msg = "Failed"
        raise Exception(msg)  # noqa: TRY002 # pylint: disable=broad-exception-raised

    app.dependency_overrides[get_health_checks] = lambda: [
        HealthCheck(name="check_1", check=success_check),
        HealthCheck(name="check_2", check=failed_check),
    ]

    response = await async_client.get("/rest/monitoring/health")

    assert response.status_code == status.HTTP_503_SERVICE_UNAVAILABLE
    assert response.json() == {
        "check_1": "OK",
        "check_2": "Failed",
    }