from pydantic import BaseModel


class CelerySettings(BaseModel):
    broker_url: str
    result_backend: str
