from pydantic_settings import BaseSettings, SettingsConfigDict

from backend.config.app import APPSettings
from backend.config.db import DBSettings
from backend.config.email import EmailSettings
from backend.config.user import UserSettings
from backend.config.worker import WorkerSettings


class Settings(BaseSettings):
    app: APPSettings = APPSettings()
    db: DBSettings
    worker: WorkerSettings
    user: UserSettings
    email: EmailSettings

    model_config = SettingsConfigDict(env_nested_delimiter="__")


_settings = Settings()


def get_settings() -> Settings:
    return _settings
