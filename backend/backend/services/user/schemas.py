from collections.abc import Callable

from pydantic import (
    BaseModel,
    EmailStr,
    Field,
    FieldValidationInfo,
    SecretStr,
    field_validator,
)

from backend.config.settings import get_settings

user_settings = get_settings().user

PasswordHasher = Callable[[str], str]


def hash_password(password: str, info: FieldValidationInfo) -> str:
    password_hasher: PasswordHasher = info.data["password_hasher"]
    return password_hasher(password)


class UserCreateSchema(BaseModel):
    email: EmailStr
    password: SecretStr = Field(min_length=user_settings.password_min_length)


class UserUpdateSchema(BaseModel):
    email: EmailStr | None = None


class Credentials(BaseModel):
    email: str
    password: SecretStr


class ResetPasswordData(BaseModel):
    token: str
    password_hasher: PasswordHasher = Field(exclude=True)
    hashed_password: str = Field(
        min_length=user_settings.password_min_length, alias="password"
    )

    hash_password = field_validator("hashed_password", mode="after")(hash_password)


class ChangePasswordData(BaseModel):
    password_hasher: PasswordHasher = Field(exclude=True)
    current_password: SecretStr
    hashed_password: str = Field(
        min_length=user_settings.password_min_length, alias="new_password"
    )

    hash_password = field_validator("hashed_password", mode="after")(hash_password)
