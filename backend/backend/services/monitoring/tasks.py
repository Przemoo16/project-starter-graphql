from typing import Literal

from backend.celery import celery_app


@celery_app.task  # type: ignore[misc]
def check_health_task() -> Literal[True]:
    return True
