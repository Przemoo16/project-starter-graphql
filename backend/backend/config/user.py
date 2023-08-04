from datetime import timedelta

from pydantic import BaseModel, SecretStr


class UserSettings(BaseModel):
    password_min_length: int = 8
    full_name_min_length: int = 1
    full_name_max_length: int = 128
    email_confirmation_url_template: str
    reset_password_url_template: str
    email_confirmation_token_lifetime: timedelta = timedelta(days=7)
    reset_password_token_lifetime: timedelta = timedelta(days=3)
    access_token_lifetime: timedelta = timedelta(minutes=30)
    refresh_token_lifetime: timedelta = timedelta(days=7)

    auth_private_key: SecretStr
    auth_public_key: str
