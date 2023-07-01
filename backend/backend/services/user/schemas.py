from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime

from pydantic import (
    BaseModel,
    EmailStr,
    Field,
    FieldValidationInfo,
    SecretStr,
    field_validator,
    model_validator,
)

from backend.config.settings import get_settings

settings = get_settings()

PasswordHasher = Callable[[str], str]


class UserCreateData(BaseModel):
    email: EmailStr
    password_hasher: PasswordHasher = Field(exclude=True)
    hashed_password: str = Field(
        min_length=settings.user.password_min_length, alias="password"
    )

    @field_validator("hashed_password", mode="after")
    def hash_password(  # pylint: disable=no-self-argument
        cls,  # noqa: N805
        plain_password: str,
        info: FieldValidationInfo,
    ) -> str:
        password_hasher: PasswordHasher = info.data["password_hasher"]
        return password_hasher(plain_password)


class UserUpdateData(BaseModel):
    email: EmailStr | None = None
    password: SecretStr | None = Field(
        default=None, min_length=settings.user.password_min_length, exclude=True
    )
    password_hasher: PasswordHasher | None = Field(default=None, exclude=True)
    hashed_password: str | None = None
    confirmed_email: bool | None = None
    last_login: datetime | None = None

    @model_validator(mode="after")  # type: ignore[arg-type]
    def hash_password(  # pylint: disable=no-self-argument
        cls,  # noqa: N805
        model: "UserUpdateData",
    ) -> "UserUpdateData":
        if not model.password:
            return model
        if not model.password_hasher:
            msg = "Missing password hasher"
            raise ValueError(msg)
        if model.hashed_password:
            msg = "Either 'password' or 'hashed_password' can be specified, not both."
            raise ValueError(msg)
        model.hashed_password = model.password_hasher(model.password.get_secret_value())
        return model


class UserFilters(BaseModel):
    email: str | None = None


@dataclass
class Credentials:
    email: str
    password: str
