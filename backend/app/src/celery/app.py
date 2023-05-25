from celery import Celery

from src.config.settings import get_settings

settings = get_settings()

app = Celery(
    "celery",
    broker=settings.celery.broker_url,
    backend=settings.celery.result_backend,
    include=["src.tasks"],
)
