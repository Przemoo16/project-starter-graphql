import logging
from collections.abc import Awaitable, Callable, Iterable, Mapping
from dataclasses import dataclass

from backend.services.monitoring.exceptions import HealthError

logger = logging.getLogger(__name__)

HEALTHY_FLAG = "OK"


@dataclass
class HealthCheck:
    name: str
    check: Callable[[], Awaitable[None]]


async def check_health(checks: Iterable[HealthCheck]) -> dict[str, str]:
    report = await _get_health_report(checks)
    validate_health(report)
    return report


async def _get_health_report(checks: Iterable[HealthCheck]) -> dict[str, str]:
    return {check.name: await _get_check_message(check) for check in checks}


async def _get_check_message(check: HealthCheck) -> str:
    try:
        await check.check()
    except Exception as exc:  # pylint: disable=broad-exception-caught
        logging.exception("The %r check failed", check.name)
        return str(exc)
    return HEALTHY_FLAG


def validate_health(report: Mapping[str, str]) -> None:
    if any(health != HEALTHY_FLAG for health in report.values()):
        raise HealthError(dict(report))
