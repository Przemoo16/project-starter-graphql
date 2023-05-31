from functools import lru_cache

from pydantic import BaseSettings

from backend.config.celery import CelerySettings
from backend.config.db import DBSettings


class Settings(BaseSettings):
    db: DBSettings
    celery: CelerySettings

    class Config:
        env_nested_delimiter = "__"


@lru_cache
def get_settings() -> Settings:
    return Settings()