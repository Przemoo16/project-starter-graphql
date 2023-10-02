from pydantic import BaseModel


class WorkerSettings(BaseModel):
    broker_url: str
    result_backend: str
