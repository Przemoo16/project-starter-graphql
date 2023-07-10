from collections.abc import Mapping
from contextlib import suppress
from uuid import UUID

import pytest

from backend.services.user.exceptions import (
    InvalidPasswordError,
    UserNotConfirmedError,
    UserNotFoundError,
)
from backend.services.user.models import User
from backend.services.user.operations.auth import (
    authenticate,
    create_access_token,
    create_refresh_token,
    login,
)
from backend.services.user.schemas import Credentials
from tests.unit.helpers.user import UserCRUD, create_confirmed_user, create_user


def success_password_validator(*_: str) -> tuple[bool, None]:
    return True, None


def get_test_password(_: str) -> str:
    return "hashed_password"


@pytest.mark.anyio()
async def test_login() -> None:
    user = create_user()
    crud = UserCRUD()

    def create_test_access_token(_: Mapping[str, str]) -> str:
        return "access-token"

    def create_test_refresh_token(_: Mapping[str, str]) -> str:
        return "refresh-token"

    access_token, refresh_token = await login(
        user, create_test_access_token, create_test_refresh_token, crud
    )

    assert access_token == "access-token"
    assert refresh_token == "refresh-token"


@pytest.mark.anyio()
async def test_login_update_last_login() -> None:
    user = create_user(last_login=False)
    crud = UserCRUD()

    def create_test_access_token(_: Mapping[str, str]) -> str:
        return "access-token"

    def create_test_refresh_token(_: Mapping[str, str]) -> str:
        return "refresh-token"

    await login(user, create_test_access_token, create_test_refresh_token, crud)

    assert user.last_login


@pytest.mark.anyio()
async def test_success_authentication_without_password_hash_update() -> None:
    credentials = Credentials(email="test@email.com", password="plain_password")
    crud = UserCRUD(
        existing_user=create_confirmed_user(
            email="test@email.com", hashed_password="hashed_password"
        )
    )

    user = await authenticate(
        credentials, success_password_validator, get_test_password, crud
    )

    assert user.hashed_password == "hashed_password"


@pytest.mark.anyio()
async def test_success_authentication_with_password_hash_update() -> None:
    credentials = Credentials(email="test@email.com", password="plain_password")
    crud = UserCRUD(
        existing_user=create_confirmed_user(
            email="test@email.com", hashed_password="hashed_password"
        )
    )

    def password_validator_update_hash(*_: str) -> tuple[bool, str]:
        return True, "new_hashed_password"

    user = await authenticate(
        credentials, password_validator_update_hash, get_test_password, crud
    )

    assert user.hashed_password == "new_hashed_password"


@pytest.mark.anyio()
async def test_failure_authentication_user_not_found() -> None:
    credentials = Credentials(email="test@email.com", password="plain_password")
    crud = UserCRUD()

    with pytest.raises(UserNotFoundError):
        await authenticate(
            credentials, success_password_validator, get_test_password, crud
        )


@pytest.mark.anyio()
@pytest.mark.parametrize(
    ("user", "hasher_called"),
    [
        (
            create_confirmed_user(email="test@email.com"),
            False,
        ),
        (None, True),
    ],
)
async def test_authentication_calling_password_hasher(
    user: User | None, hasher_called: bool
) -> None:
    credentials = Credentials(email="test@email.com", password="plain_password")
    crud = UserCRUD(existing_user=user)

    hash_function_called = False

    def hash_password(_: str) -> str:
        nonlocal hash_function_called
        hash_function_called = True
        return "hashed_password"

    with suppress(UserNotFoundError):
        await authenticate(credentials, success_password_validator, hash_password, crud)

    assert hash_function_called == hasher_called


@pytest.mark.anyio()
async def test_failure_authentication_invalid_password() -> None:
    credentials = Credentials(email="test@email.com", password="plain_password")
    crud = UserCRUD(existing_user=create_confirmed_user(email="test@email.com"))

    def failure_validator(*_: str) -> tuple[bool, None]:
        return False, None

    with pytest.raises(InvalidPasswordError):
        await authenticate(credentials, failure_validator, get_test_password, crud)


@pytest.mark.anyio()
async def test_failure_authentication_user_not_confirmed() -> None:
    credentials = Credentials(email="test@email.com", password="plain_password")
    crud = UserCRUD(existing_user=create_user(email="test@email.com"))

    with pytest.raises(UserNotConfirmedError):
        await authenticate(
            credentials, success_password_validator, get_test_password, crud
        )


def test_create_access_token() -> None:
    user_id = UUID("6d9c79d6-9641-4746-92d9-2cc9ebdca941")

    def create_token(payload: Mapping[str, str]) -> str:
        return f"sub:{payload['sub']}-type:{payload['type']}"

    token = create_access_token(user_id, create_token)

    assert token == "sub:6d9c79d6-9641-4746-92d9-2cc9ebdca941-type:access"


def test_create_refresh_token() -> None:
    user_id = UUID("6d9c79d6-9641-4746-92d9-2cc9ebdca941")

    def create_token(payload: Mapping[str, str]) -> str:
        return f"sub:{payload['sub']}-type:{payload['type']}"

    token = create_refresh_token(user_id, create_token)

    assert token == "sub:6d9c79d6-9641-4746-92d9-2cc9ebdca941-type:refresh"
