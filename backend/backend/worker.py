from celery import Celery

from backend.config.settings import get_settings

worker_settings = get_settings().worker

worker_app = Celery(
    "celery",
    broker=worker_settings.broker_url,
    backend=worker_settings.result_backend,
)
worker_app.autodiscover_tasks(["backend.services.monitoring", "backend.services.user"])
