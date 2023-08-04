from pydantic import BaseModel, EmailStr, Field, SecretStr

from backend.config.settings import get_settings

user_settings = get_settings().user


class UserCreateSchema(BaseModel):
    email: EmailStr
    password: SecretStr = Field(min_length=user_settings.password_min_length)
    full_name: str = Field(
        min_length=user_settings.full_name_min_length,
        max_length=user_settings.full_name_max_length,
    )


class UserUpdateSchema(BaseModel):
    full_name: str | None = Field(
        default=None,
        min_length=user_settings.full_name_min_length,
        max_length=user_settings.full_name_max_length,
    )


class CredentialsSchema(BaseModel):
    email: str
    password: SecretStr


class PasswordResetSchema(BaseModel):
    token: str
    password: SecretStr = Field(min_length=user_settings.password_min_length)


class PasswordChangeSchema(BaseModel):
    current_password: SecretStr
    new_password: SecretStr = Field(min_length=user_settings.password_min_length)
