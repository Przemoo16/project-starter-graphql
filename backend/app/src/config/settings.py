from functools import lru_cache

from pydantic import BaseSettings

from src.config.db import DBSettings


class Settings(BaseSettings):
    db: DBSettings

    class Config:
        env_nested_delimiter = "__"


@lru_cache
def get_settings() -> Settings:
    return Settings()
