from collections.abc import Callable
from typing import Any

from pydantic import BaseModel, EmailStr, Field, validator
from pydantic.main import ModelMetaclass

from backend.config.settings import get_settings
from backend.libs.security.password import hash_password

settings = get_settings()


def hash_password_validator(
    cls: ModelMetaclass,  # pylint: disable=unused-argument
    password: str,
    values: dict[str, Any],
) -> str:
    algorithm: Callable[[str], str] = values["hash_password_algorithm"]
    return algorithm(password)


class UserCreateData(BaseModel):
    email: EmailStr
    hash_password_algorithm: Callable[[str], str] = Field(
        default=hash_password, exclude=True
    )
    hashed_password: str = Field(
        min_length=settings.user.password_min_length, alias="password"
    )

    _hash_password = validator("hashed_password", allow_reuse=True)(
        hash_password_validator
    )


class UserUpdateData(BaseModel):
    email: EmailStr | None = None
    hash_password_algorithm: Callable[[str], str] = Field(
        default=hash_password, exclude=True
    )
    hashed_password: str | None = Field(
        default=None, min_length=settings.user.password_min_length, alias="password"
    )
    confirmed_email: bool | None = None

    _hash_password = validator("hashed_password", allow_reuse=True)(
        hash_password_validator
    )


class UserFilters(BaseModel):
    email: str | None = None
