from pydantic import BaseSettings

from backend.config.app import APPSettings
from backend.config.celery import CelerySettings
from backend.config.db import DBSettings
from backend.config.email import EmailSettings
from backend.config.user import UserSettings


class Settings(BaseSettings):
    app: APPSettings = APPSettings()
    db: DBSettings
    celery: CelerySettings
    user: UserSettings
    email: EmailSettings

    class Config:
        env_nested_delimiter = "__"


_settings = Settings()


def get_settings() -> Settings:
    return _settings
