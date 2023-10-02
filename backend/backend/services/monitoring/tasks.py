from typing import Literal

from backend.worker import worker_app


@worker_app.task  # type: ignore[misc]
def check_health_task() -> Literal[True]:
    return True
