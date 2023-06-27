from pydantic import BaseModel, SecretStr
from sqlalchemy.engine import URL


class DBSettings(BaseModel):
    password: str
    username: SecretStr
    name: str
    host: str
    port: int
    driver: str = "postgresql+asyncpg"

    @property
    def url(self) -> URL:
        return URL.create(
            drivername=self.driver,
            username=self.username.get_secret_value(),
            password=self.password,
            host=self.host,
            port=self.port,
            database=self.name,
        )
