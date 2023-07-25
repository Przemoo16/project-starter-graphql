from collections.abc import Callable
from datetime import datetime
from uuid import UUID

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

user_settings = get_settings().user

PasswordHasher = Callable[[str], str]


def hash_password(password: str, info: FieldValidationInfo) -> str:
    password_hasher: PasswordHasher = info.data["password_hasher"]
    return password_hasher(password)


class UserCreateData(BaseModel):
    email: EmailStr
    password_hasher: PasswordHasher = Field(exclude=True)
    hashed_password: str = Field(
        min_length=user_settings.password_min_length, alias="password"
    )

    hash_password = field_validator("hashed_password", mode="after")(hash_password)


class UserUpdateData(BaseModel):
    email: EmailStr | None = None
    password: SecretStr | None = Field(
        default=None, min_length=user_settings.password_min_length, exclude=True
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
    id: UUID | None = None
    email: str | None = None


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
