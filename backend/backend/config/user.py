from pydantic import AnyHttpUrl, BaseModel


class UserSettings(BaseModel):
    password_min_length: int = 8
    email_confirmation_url: AnyHttpUrl
