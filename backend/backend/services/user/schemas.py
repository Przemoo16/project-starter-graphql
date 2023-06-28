from collections.abc import Callable
from typing import Any

from pydantic import BaseModel, EmailStr, Field, SecretStr, validator

from backend.config.settings import get_settings

settings = get_settings()

PasswordHasher = Callable[[str], str]


class UserCreateData(BaseModel):
    email: EmailStr
    password_hasher: PasswordHasher = Field(exclude=True)
    hashed_password: str = Field(
        min_length=settings.user.password_min_length, alias="password"
    )

    @validator("hashed_password")
    def hash_password(  # pylint: disable=no-self-argument
        cls,  # noqa: N805
        plain_password: str,
        values: dict[str, Any],
    ) -> str:
        password_hasher: PasswordHasher = values["password_hasher"]
        return password_hasher(plain_password)


class UserUpdateData(BaseModel):
    email: EmailStr | None = None
    password: SecretStr | None = Field(
        default=None, min_length=settings.user.password_min_length, exclude=True
    )
    password_hasher: PasswordHasher | None = Field(default=None, exclude=True)
    hashed_password: str | None = None
    confirmed_email: bool | None = None

    @validator("hashed_password", always=True)
    def hash_password(  # pylint: disable=no-self-argument
        cls,  # noqa: N805
        hashed_password: str | None,
        values: dict[str, Any],
    ) -> str | None:
        if hashed_password:
            return hashed_password
        plain_password: SecretStr | None = values.get("password")
        if not plain_password:
            return None
        password_hasher = cls._get_password_hasher(values)
        return password_hasher(plain_password.get_secret_value())

    @staticmethod
    def _get_password_hasher(values: dict[str, Any]) -> PasswordHasher:
        password_hasher: PasswordHasher | None = values.get("password_hasher")
        if not password_hasher:
            msg = "Missing password hasher"
            raise ValueError(msg)
        return password_hasher


class UserFilters(BaseModel):
    email: str | None = None


class Credentials(BaseModel):
    email: str
    password: str
