from pydantic import BaseModel, EmailStr, Field

from backend.config.settings import settings

_user_settings = settings.user


class UserCreateSchema(BaseModel):
    email: EmailStr
    password: str = Field(min_length=_user_settings.password_min_length)
    full_name: str = Field(
        min_length=_user_settings.full_name_min_length,
        max_length=_user_settings.full_name_max_length,
    )


class UserUpdateSchema(BaseModel):
    full_name: str | None = Field(
        default=None,
        min_length=_user_settings.full_name_min_length,
        max_length=_user_settings.full_name_max_length,
    )


class CredentialsSchema(BaseModel):
    email: str
    password: str


class PasswordResetSchema(BaseModel):
    token: str
    password: str = Field(min_length=_user_settings.password_min_length)


class PasswordChangeSchema(BaseModel):
    current_password: str
    new_password: str = Field(min_length=_user_settings.password_min_length)
