from pydantic_settings import BaseSettings, SettingsConfigDict

from backend.config.app import APPSettings
from backend.config.db import DBSettings
from backend.config.email import EmailSettings
from backend.config.monitoring import MonitoringSettings
from backend.config.user import UserSettings
from backend.config.worker import WorkerSettings


class Settings(BaseSettings):
    app: APPSettings = APPSettings()
    db: DBSettings
    worker: WorkerSettings
    email: EmailSettings

    user: UserSettings
    monitoring: MonitoringSettings = MonitoringSettings()

    model_config = SettingsConfigDict(env_nested_delimiter="__")


_settings = Settings()


def get_settings() -> Settings:
    return _settings
