from datetime import timedelta

from pydantic import BaseModel


class MonitoringSettings(BaseModel):
    worker_health_check_timeout: timedelta = timedelta(seconds=5)
