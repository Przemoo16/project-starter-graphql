from typing import Any

import pytest
from pydantic import ValidationError

from backend.services.user.schemas import (
    ResetPasswordData,
    UserCreateData,
    UserUpdateData,
)


def get_test_password(_: str) -> str:
    return "hashed_password"


@pytest.mark.parametrize(
    ("schema", "params"),
    [
        (UserCreateData, {"password": "plain_password"}),
        (UserUpdateData, {}),
    ],
)
def test_schema_invalid_email(
    schema: type[UserCreateData] | type[UserUpdateData], params: dict[str, Any]
) -> None:
    email = "invalid_email"

    with pytest.raises(ValidationError, match="not a valid email address") as exc_info:
        schema(email=email, password_hasher=get_test_password, **params)
    assert len(exc_info.value.errors()) == 1


@pytest.mark.parametrize(
    ("schema", "params"),
    [
        (UserCreateData, {"email": "test@email.com"}),
        (UserUpdateData, {}),
        (ResetPasswordData, {"token": "test-token"}),
    ],
)
def test_schema_password_too_short(
    schema: type[UserCreateData] | type[UserUpdateData], params: dict[str, Any]
) -> None:
    password = "p"

    with pytest.raises(ValidationError, match="too_short") as exc_info:
        schema(password=password, password_hasher=get_test_password, **params)
    assert len(exc_info.value.errors()) == 1


@pytest.mark.parametrize(
    ("schema", "params"),
    [
        (UserCreateData, {"email": "test@email.com"}),
        (UserUpdateData, {}),
        (ResetPasswordData, {"token": "test-token"}),
    ],
)
def test_schema_does_not_export_password_related_fields(
    schema: type[UserCreateData] | type[UserUpdateData], params: dict[str, Any]
) -> None:
    password = "plain_password"

    data = schema(password=password, password_hasher=get_test_password, **params)

    data_dict = data.model_dump()
    assert "password_hasher" not in data_dict
    assert "password" not in data_dict


@pytest.mark.parametrize(
    ("schema", "params"),
    [
        (UserCreateData, {"email": "test@email.com"}),
        (UserUpdateData, {}),
        (ResetPasswordData, {"token": "test-token"}),
    ],
)
def test_schema_hashes_password(
    schema: type[UserCreateData] | type[UserUpdateData], params: dict[str, Any]
) -> None:
    password = "plain_password"

    def hash_password(_: str) -> str:
        return "hashed_password"

    data = schema(password=password, password_hasher=hash_password, **params)

    assert data.hashed_password == "hashed_password"


def test_user_update_schema_hashed_password_directly_provided() -> None:
    hashed_password = "hashed_password"

    data = UserUpdateData(hashed_password=hashed_password)

    assert data.hashed_password == "hashed_password"


def test_user_update_schema_no_password_provided() -> None:
    data = UserUpdateData()

    assert not data.hashed_password


def test_user_update_schema_missing_password_hasher() -> None:
    password = "plain_password"

    with pytest.raises(ValidationError, match="Missing password hasher") as exc_info:
        UserUpdateData(password=password)
    assert len(exc_info.value.errors()) == 1


def test_user_update_schema_both_password_and_hash_password_present() -> None:
    password = "plain_password"
    hashed_password = "hashed_password"

    with pytest.raises(
        ValidationError,
        match="Either 'password' or 'hashed_password' can be specified, not both.",
    ) as exc_info:
        UserUpdateData(
            password=password,
            hashed_password=hashed_password,
            password_hasher=get_test_password,
        )
    assert len(exc_info.value.errors()) == 1
