import pytest
from pydantic import ValidationError

from backend.services.user.schemas import (
    PasswordChangeSchema,
    PasswordResetSchema,
    UserCreateSchema,
    UserUpdateSchema,
)


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


def test_password_reset_password_too_short() -> None:
    with pytest.raises(ValidationError, match="too_short") as exc_info:
        PasswordResetSchema(token="test-token", password="p")
    assert len(exc_info.value.errors()) == 1


def test_password_schange_password_too_short() -> None:
    with pytest.raises(ValidationError, match="too_short") as exc_info:
        PasswordChangeSchema(current_password="plain_password", new_password="p")
    assert len(exc_info.value.errors()) == 1
