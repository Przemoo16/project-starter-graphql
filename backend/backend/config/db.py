from pydantic import BaseModel
from sqlalchemy.engine import URL


class DBSettings(BaseModel):
    password: str
    username: str = "postgres"
    name: str = "postgres"
    host: str = "db"
    port: int = 5432
    driver: str = "postgresql+asyncpg"

    @property
    def url(self) -> URL:
        return URL.create(
            drivername=self.driver,
            username=self.username,
            password=self.password,
            host=self.host,
            port=self.port,
            database=self.name,
        )
