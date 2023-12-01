import pytest

from backend.services.monitoring.exceptions import HealthError
from backend.services.monitoring.operations.health import HealthCheck, check_health


@pytest.mark.anyio()
async def test_check_health_healthy() -> None:
    async def success_check() -> None:
        pass

    checks = [
        HealthCheck(name="check_1", check=success_check),
        HealthCheck(name="check_2", check=success_check),
    ]

    health = await check_health(checks)

    assert health == {
        "check_1": "OK",
        "check_2": "OK",
    }


@pytest.mark.anyio()
async def test_check_health_unhealthy() -> None:
    async def success_check() -> None:
        pass

    async def failed_check() -> None:
        msg = "Failed"
        raise Exception(msg)  # noqa: TRY002

    checks = [
        HealthCheck(name="check_1", check=success_check),
        HealthCheck(name="check_2", check=failed_check),
    ]

    with pytest.raises(HealthError) as exc_info:
        await check_health(checks)

    assert exc_info.value.report == {
        "check_1": "OK",
        "check_2": "Failed",
    }
