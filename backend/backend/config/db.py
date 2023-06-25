from pydantic import BaseModel
from sqlalchemy.engine import URL


class DBSettings(BaseModel):
    password: str
    username: str
    name: str
    host: str
    port: int
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
