from collections.abc import Mapping
from typing import Any

import pytest
from pydantic import ValidationError

from backend.services.user.schemas import (
    ChangePasswordData,
    ResetPasswordData,
    UserCreateSchema,
    UserUpdateSchema,
)

PasswordRelatedSchemas = type[ResetPasswordData] | type[ChangePasswordData]


def get_test_password(_: str) -> str:
    return "hashed_password"


def test_user_create_invalid_email() -> None:
    with pytest.raises(ValidationError, match="not a valid email address") as exc_info:
        UserCreateSchema(email="invalid_email", password="plain_password")
    assert len(exc_info.value.errors()) == 1


def test_user_create_password_too_short() -> None:
    with pytest.raises(ValidationError, match="too_short") as exc_info:
        UserCreateSchema(email="test@email.com", password="p")
    assert len(exc_info.value.errors()) == 1


def test_user_update_invalid_email() -> None:
    with pytest.raises(ValidationError, match="not a valid email address") as exc_info:
        UserUpdateSchema(email="invalid_email")
    assert len(exc_info.value.errors()) == 1


@pytest.mark.parametrize(
    ("schema", "password_field", "params"),
    [
        (ResetPasswordData, "password", {"token": "test-token"}),
        (ChangePasswordData, "new_password", {"current_password": "plain_password"}),
    ],
)
def test_schema_password_too_short(
    schema: PasswordRelatedSchemas, password_field: str, params: Mapping[str, Any]
) -> None:
    schema_params = {password_field: "p", **params}

    with pytest.raises(ValidationError, match="too_short") as exc_info:
        schema(password_hasher=get_test_password, **schema_params)
    assert len(exc_info.value.errors()) == 1


@pytest.mark.parametrize(
    ("schema", "password_field", "params"),
    [
        (ResetPasswordData, "password", {"token": "test-token"}),
        (ChangePasswordData, "new_password", {"current_password": "plain_password"}),
    ],
)
def test_schema_does_not_export_password_related_fields(
    schema: PasswordRelatedSchemas, password_field: str, params: Mapping[str, Any]
) -> None:
    schema_params = {password_field: "plain_password", **params}

    data = schema(password_hasher=get_test_password, **schema_params)

    data_dict = data.model_dump()
    assert "password_hasher" not in data_dict
    assert "password" not in data_dict


@pytest.mark.parametrize(
    ("schema", "password_field", "params"),
    [
        (ResetPasswordData, "password", {"token": "test-token"}),
        (ChangePasswordData, "new_password", {"current_password": "plain_password"}),
    ],
)
def test_schema_hashes_password(
    schema: PasswordRelatedSchemas, password_field: str, params: Mapping[str, Any]
) -> None:
    schema_params = {password_field: "plain_password", **params}

    def hash_password(_: str) -> str:
        return "hashed_password"

    data = schema(password_hasher=hash_password, **schema_params)

    assert data.hashed_password == "hashed_password"
