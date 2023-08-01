from collections.abc import Mapping
from typing import Any
from uuid import UUID

import pytest

from backend.libs.security.token import InvalidTokenError
from backend.services.user.exceptions import (
    InvalidAccessTokenError,
    InvalidPasswordError,
    InvalidRefreshTokenError,
    UserNotConfirmedError,
    UserNotFoundError,
)
from backend.services.user.operations.auth import (
    PasswordManager,
    TokensManager,
    get_confirmed_user_by_id,
    login,
    read_access_token,
    read_refresh_token,
)
from backend.services.user.schemas import CredentialsSchema
from tests.unit.helpers.user import UserCRUD, create_confirmed_user, create_user


@pytest.fixture(name="password_manager")
def password_manager_fixture() -> PasswordManager:
    def validate_password(*_: str) -> tuple[bool, None]:
        return True, None

    def hash_password(_: str) -> str:
        return "hashed_password"

    return PasswordManager(validator=validate_password, hasher=hash_password)


@pytest.fixture(name="tokens_manager")
def tokens_manager_fixture() -> TokensManager:
    def create_token(_: Mapping[str, Any]) -> str:
        return "test-token"

    return TokensManager(
        access_token_creator=create_token, refresh_token_creator=create_token
    )


@pytest.mark.anyio()
async def test_login_create_tokens(password_manager: PasswordManager) -> None:
    credentials = CredentialsSchema(email="test@email.com", password="plain_password")

    def create_token(payload: Mapping[str, Any]) -> str:
        return "-".join(f"{key}:{value}" for key, value in payload.items())

    tokens_manager = TokensManager(
        access_token_creator=create_token,
        refresh_token_creator=create_token,
    )
    crud = UserCRUD(
        existing_user=create_confirmed_user(
            id=UUID("6d9c79d6-9641-4746-92d9-2cc9ebdca941"), email="test@email.com"
        )
    )

    access_token, refresh_token = await login(
        credentials, password_manager, tokens_manager, crud
    )

    assert access_token == "sub:6d9c79d6-9641-4746-92d9-2cc9ebdca941-type:access"
    assert refresh_token == "sub:6d9c79d6-9641-4746-92d9-2cc9ebdca941-type:refresh"


@pytest.mark.anyio()
async def test_login_update_password_hash(
    password_manager: PasswordManager, tokens_manager: TokensManager
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
    password_manager: PasswordManager, tokens_manager: TokensManager
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
    password_manager: PasswordManager, tokens_manager: TokensManager
) -> None:
    credentials = CredentialsSchema(email="test@email.com", password="plain_password")
    user = create_confirmed_user(email="test@email.com", last_login=None)
    crud = UserCRUD(existing_user=user)

    await login(credentials, password_manager, tokens_manager, crud)

    assert user.last_login


@pytest.mark.anyio()
async def test_login_user_not_found(
    password_manager: PasswordManager, tokens_manager: TokensManager
) -> None:
    credentials = CredentialsSchema(email="test@email.com", password="plain_password")
    crud = UserCRUD()

    with pytest.raises(UserNotFoundError):
        await login(credentials, password_manager, tokens_manager, crud)


async def test_login_user_not_found_password_hasher_called(
    password_manager: PasswordManager, tokens_manager: TokensManager
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
    password_manager: PasswordManager, tokens_manager: TokensManager
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
    password_manager: PasswordManager, tokens_manager: TokensManager
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
    password_manager: PasswordManager, tokens_manager: TokensManager
) -> None:
    credentials = CredentialsSchema(email="test@email.com", password="plain_password")
    crud = UserCRUD(existing_user=create_user(email="test@email.com"))

    with pytest.raises(UserNotConfirmedError):
        await login(credentials, password_manager, tokens_manager, crud)


################################################## TODO: Continue refactoring


def test_read_access_token() -> None:
    token = "test-token"

    def read_token(_: str) -> dict[str, str]:
        return {
            "sub": "6d9c79d6-9641-4746-92d9-2cc9ebdca941",
            "type": "access",
        }

    payload = read_access_token(token, read_token)

    assert payload.user_id == UUID("6d9c79d6-9641-4746-92d9-2cc9ebdca941")


def test_read_access_token_invalid_token() -> None:
    token = "test-token"

    def read_token(_: str) -> dict[str, str]:
        raise InvalidTokenError

    with pytest.raises(InvalidAccessTokenError):
        read_access_token(token, read_token)


def test_read_access_token_invalid_token_type() -> None:
    token = "test-token"

    def read_token(_: str) -> dict[str, str]:
        return {
            "sub": "6d9c79d6-9641-4746-92d9-2cc9ebdca941",
            "type": "invalid-type",
        }

    with pytest.raises(InvalidAccessTokenError):
        read_access_token(token, read_token)


@pytest.mark.anyio()
async def test_get_confirmed_user_by_id() -> None:
    user_id = UUID("6d9c79d6-9641-4746-92d9-2cc9ebdca941")
    user = create_confirmed_user(id=user_id)
    crud = UserCRUD(existing_user=user)

    confirmed_user = await get_confirmed_user_by_id(user_id, crud)

    assert confirmed_user == user


@pytest.mark.anyio()
async def test_get_confirmed_user_by_id_user_not_found() -> None:
    user_id = UUID("6d9c79d6-9641-4746-92d9-2cc9ebdca941")
    crud = UserCRUD()

    with pytest.raises(UserNotFoundError):
        await get_confirmed_user_by_id(user_id, crud)


@pytest.mark.anyio()
async def test_get_confirmed_user_by_id_user_not_confirmed() -> None:
    user_id = UUID("6d9c79d6-9641-4746-92d9-2cc9ebdca941")
    crud = UserCRUD(existing_user=create_user(id=user_id))

    with pytest.raises(UserNotConfirmedError):
        await get_confirmed_user_by_id(user_id, crud)


def test_read_refresh_token() -> None:
    token = "test-token"

    def read_token(_: str) -> dict[str, str]:
        return {
            "sub": "6d9c79d6-9641-4746-92d9-2cc9ebdca941",
            "type": "refresh",
        }

    payload = read_refresh_token(token, read_token)

    assert payload.user_id == UUID("6d9c79d6-9641-4746-92d9-2cc9ebdca941")


def test_read_refresh_token_invalid_token() -> None:
    token = "test-token"

    def read_token(_: str) -> dict[str, str]:
        raise InvalidTokenError

    with pytest.raises(InvalidRefreshTokenError):
        read_refresh_token(token, read_token)


def test_read_refresh_token_invalid_token_type() -> None:
    token = "test-token"

    def read_token(_: str) -> dict[str, str]:
        return {
            "sub": "6d9c79d6-9641-4746-92d9-2cc9ebdca941",
            "type": "invalid-type",
        }

    with pytest.raises(InvalidRefreshTokenError):
        read_refresh_token(token, read_token)
