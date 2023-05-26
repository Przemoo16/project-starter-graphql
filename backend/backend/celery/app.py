from celery import Celery

from backend.config.settings import get_settings

settings = get_settings()

app = Celery(
    "backend",
    broker=settings.celery.broker_url,
    backend=settings.celery.result_backend,
    include=["backend.tasks"],
)
