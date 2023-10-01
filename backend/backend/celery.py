from celery import Celery

from backend.config.settings import get_settings

celery_settings = get_settings().celery

celery_app = Celery(
    "celery",
    broker=celery_settings.broker_url,
    backend=celery_settings.result_backend,
)
celery_app.autodiscover_tasks(["backend.services.monitoring", "backend.services.user"])
