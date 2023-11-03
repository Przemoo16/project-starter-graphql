from celery import Celery

from backend.config.settings import settings

_worker_settings = settings.worker

worker_app = Celery(
    "celery",
    broker=_worker_settings.broker_url,
    backend=_worker_settings.result_backend,
)
worker_app.autodiscover_tasks(["backend.services.monitoring", "backend.services.user"])
