from pydantic import BaseModel


class APPSettings(BaseModel):
    dev_mode: bool = False
