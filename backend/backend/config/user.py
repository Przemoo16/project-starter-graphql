from pydantic import BaseModel


class UserSettings(BaseModel):
    password_min_length: int = 8
