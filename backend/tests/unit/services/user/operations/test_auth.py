from collections.abc import Mapping
from typing import Any
from uuid import UUID

import pytest

from backend.libs.security.token import InvalidTokenError
from backend.services.user.exceptions import (
    InvalidAccessTokenError,
    InvalidPasswordError,
    InvalidRefreshTokenError,
    MissingAccessTokenError,
    UserNotConfirmedError,
    UserNotFoundError,
)
from backend.services.user.operations.auth import (
    AuthTokensManager,
    PasswordManager,
    get_confirmed_user_from_headers,
    login,
    refresh_token,
)
from backend.services.user.schemas import CredentialsSchema
from tests.unit.helpers.user import UserCRUD, create_confirmed_user, create_user


def create_test_token(_: Mapping[str, Any]) -> str:
    return "test-token"


@pytest.fixture(name="password_manager")
def password_manager_fixture() -> PasswordManager:
    def validate_password(*_: str) -> tuple[bool, None]:
        return True, None

    def hash_password(_: str) -> str:
        return "hashed_password"

    return PasswordManager(validator=validate_password, hasher=hash_password)


@pytest.fixture(name="tokens_manager")
def tokens_manager_fixture() -> AuthTokensManager:
    return AuthTokensManager(
        access_token_creator=create_test_token, refresh_token_creator=create_test_token
    )


@pytest.mark.anyio()
async def test_login_create_tokens(password_manager: PasswordManager) -> None:
    credentials = CredentialsSchema(email="test@email.com", password="plain_password")

    def create_token(payload: Mapping[str, Any]) -> str:
        return "-".join(f"{key}:{value}" for key, value in payload.items())

    tokens_manager = AuthTokensManager(
        access_token_creator=create_token,
        refresh_token_creator=create_token,
    )
    crud = UserCRUD(
        existing_user=create_confirmed_user(
            id=UUID("6d9c79d6-9641-4746-92d9-2cc9ebdca941"), email="test@email.com"
        )
    )

    access_token, refresh_token_ = await login(
        credentials, password_manager, tokens_manager, crud
    )

    assert access_token == "sub:6d9c79d6-9641-4746-92d9-2cc9ebdca941-type:access"
    assert refresh_token_ == "sub:6d9c79d6-9641-4746-92d9-2cc9ebdca941-type:refresh"


@pytest.mark.anyio()
async def test_login_update_password_hash(
    password_manager: PasswordManager, tokens_manager: AuthTokensManager
) -> None:
    credentials = CredentialsSchema(email="test@email.com", password="plain_password")

    def validate_password(*_: str) -> tuple[bool, str]:
        return True, "new_hashed_password"

    password_manager.validator = validate_password
    user = create_confirmed_user(
        email="test@email.com", hashed_password="hashed_password"
    )
    crud = UserCRUD(existing_user=user)

    await login(credentials, password_manager, tokens_manager, crud)

    assert user.hashed_password == "new_hashed_password"


@pytest.mark.anyio()
async def test_login_do_not_update_password_hash(
    password_manager: PasswordManager, tokens_manager: AuthTokensManager
) -> None:
    credentials = CredentialsSchema(email="test@email.com", password="plain_password")

    def validate_password(*_: str) -> tuple[bool, None]:
        return True, None

    password_manager.validator = validate_password
    user = create_confirmed_user(
        email="test@email.com", hashed_password="hashed_password"
    )
    crud = UserCRUD(existing_user=user)

    await login(credentials, password_manager, tokens_manager, crud)

    assert user.hashed_password == "hashed_password"


@pytest.mark.anyio()
async def test_login_update_last_login(
    password_manager: PasswordManager, tokens_manager: AuthTokensManager
) -> None:
    credentials = CredentialsSchema(email="test@email.com", password="plain_password")
    user = create_confirmed_user(email="test@email.com", last_login=None)
    crud = UserCRUD(existing_user=user)

    await login(credentials, password_manager, tokens_manager, crud)

    assert user.last_login


@pytest.mark.anyio()
async def test_login_user_not_found(
    password_manager: PasswordManager, tokens_manager: AuthTokensManager
) -> None:
    credentials = CredentialsSchema(email="test@email.com", password="plain_password")
    crud = UserCRUD()

    with pytest.raises(UserNotFoundError):
        await login(credentials, password_manager, tokens_manager, crud)


@pytest.mark.anyio()
async def test_login_user_not_found_password_hasher_called(
    password_manager: PasswordManager, tokens_manager: AuthTokensManager
) -> None:
    credentials = CredentialsSchema(email="test@email.com", password="plain_password")
    hasher_called = False

    def hash_password(_: str) -> str:
        nonlocal hasher_called
        hasher_called = True
        return "hashed_password"

    password_manager.hasher = hash_password
    crud = UserCRUD()

    with pytest.raises(UserNotFoundError):
        await login(credentials, password_manager, tokens_manager, crud)
    assert hasher_called


@pytest.mark.anyio()
async def test_login_user_found_password_hasher_not_called(
    password_manager: PasswordManager, tokens_manager: AuthTokensManager
) -> None:
    credentials = CredentialsSchema(email="test@email.com", password="plain_password")
    hasher_called = False

    def hash_password(_: str) -> str:
        nonlocal hasher_called
        hasher_called = True
        return "hashed_password"

    password_manager.hasher = hash_password
    crud = UserCRUD(existing_user=create_confirmed_user(email="test@email.com"))

    await login(credentials, password_manager, tokens_manager, crud)

    assert not hasher_called


@pytest.mark.anyio()
async def test_login_invalid_password(
    password_manager: PasswordManager, tokens_manager: AuthTokensManager
) -> None:
    credentials = CredentialsSchema(email="test@email.com", password="plain_password")

    def validate_password(*_: str) -> tuple[bool, None]:
        return False, None

    password_manager.validator = validate_password
    crud = UserCRUD(existing_user=create_confirmed_user(email="test@email.com"))

    with pytest.raises(InvalidPasswordError):
        await login(credentials, password_manager, tokens_manager, crud)


@pytest.mark.anyio()
async def test_login_user_not_confirmed(
    password_manager: PasswordManager, tokens_manager: AuthTokensManager
) -> None:
    credentials = CredentialsSchema(email="test@email.com", password="plain_password")
    crud = UserCRUD(existing_user=create_user(email="test@email.com"))

    with pytest.raises(UserNotConfirmedError):
        await login(credentials, password_manager, tokens_manager, crud)


@pytest.mark.anyio()
async def test_get_confirmed_user_from_headers() -> None:
    headers = {"Authorization": "Bearer test-token"}

    def read_token(_: str) -> dict[str, str]:
        return {
            "sub": "6d9c79d6-9641-4746-92d9-2cc9ebdca941",
            "type": "access",
        }

    crud = UserCRUD(
        existing_user=create_confirmed_user(
            id=UUID("6d9c79d6-9641-4746-92d9-2cc9ebdca941")
        )
    )

    user = await get_confirmed_user_from_headers(headers, read_token, crud)

    assert user.id == UUID("6d9c79d6-9641-4746-92d9-2cc9ebdca941")


@pytest.mark.anyio()
async def test_get_confirmed_user_from_headers_missing_token() -> None:
    headers: dict[str, str] = {}

    def read_token(_: str) -> dict[str, str]:
        return {
            "sub": "6d9c79d6-9641-4746-92d9-2cc9ebdca941",
            "type": "access",
        }

    crud = UserCRUD()

    with pytest.raises(MissingAccessTokenError):
        await get_confirmed_user_from_headers(headers, read_token, crud)


@pytest.mark.anyio()
async def test_get_confirmed_user_from_headers_invalid_token() -> None:
    headers = {"Authorization": "Bearer test-token"}

    def read_token(_: str) -> dict[str, str]:
        raise InvalidTokenError

    crud = UserCRUD()

    with pytest.raises(InvalidAccessTokenError):
        await get_confirmed_user_from_headers(headers, read_token, crud)


@pytest.mark.anyio()
async def test_get_confirmed_user_from_headers_invalid_token_type() -> None:
    headers = {"Authorization": "Bearer test-token"}

    def read_token(_: str) -> dict[str, str]:
        return {
            "sub": "6d9c79d6-9641-4746-92d9-2cc9ebdca941",
            "type": "invalid-type",
        }

    crud = UserCRUD()

    with pytest.raises(InvalidAccessTokenError):
        await get_confirmed_user_from_headers(headers, read_token, crud)


@pytest.mark.anyio()
async def test_get_confirmed_user_from_headers_user_not_found() -> None:
    headers = {"Authorization": "Bearer test-token"}

    def read_token(_: str) -> dict[str, str]:
        return {
            "sub": "6d9c79d6-9641-4746-92d9-2cc9ebdca941",
            "type": "access",
        }

    crud = UserCRUD()

    with pytest.raises(UserNotFoundError):
        await get_confirmed_user_from_headers(headers, read_token, crud)


@pytest.mark.anyio()
async def test_get_confirmed_user_from_headers_user_not_confirmed() -> None:
    headers = {"Authorization": "Bearer test-token"}

    def read_token(_: str) -> dict[str, str]:
        return {
            "sub": "6d9c79d6-9641-4746-92d9-2cc9ebdca941",
            "type": "access",
        }

    crud = UserCRUD(
        existing_user=create_user(id=UUID("6d9c79d6-9641-4746-92d9-2cc9ebdca941"))
    )

    with pytest.raises(UserNotConfirmedError):
        await get_confirmed_user_from_headers(headers, read_token, crud)


def test_refresh_token() -> None:
    token = "test-token"

    def read_token(_: str) -> dict[str, str]:
        return {
            "sub": "6d9c79d6-9641-4746-92d9-2cc9ebdca941",
            "type": "refresh",
        }

    def create_token(payload: Mapping[str, Any]) -> str:
        return "-".join(f"{key}:{value}" for key, value in payload.items())

    access_token = refresh_token(token, read_token, create_token)

    assert access_token == "sub:6d9c79d6-9641-4746-92d9-2cc9ebdca941-type:access"


def test_refresh_token_invalid_token() -> None:
    token = "test-token"

    def read_token(_: str) -> dict[str, str]:
        raise InvalidTokenError

    with pytest.raises(InvalidRefreshTokenError):
        refresh_token(token, read_token, create_test_token)


def test_refresh_token_invalid_token_type() -> None:
    token = "test-token"

    def read_token(_: str) -> dict[str, str]:
        return {
            "sub": "6d9c79d6-9641-4746-92d9-2cc9ebdca941",
            "type": "invalid-type",
        }

    with pytest.raises(InvalidRefreshTokenError):
        refresh_token(token, read_token, create_test_token)
