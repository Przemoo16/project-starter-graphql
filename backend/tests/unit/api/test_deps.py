from dataclasses import dataclass
from uuid import UUID

import pytest

from backend.api.deps import UnauthorizedError, get_confirmed_user
from backend.libs.security.token import InvalidTokenError
from tests.unit.helpers.user import UserCRUD, create_confirmed_user, create_user


@dataclass
class Request:
    headers: dict[str, str]


@pytest.mark.anyio()
async def test_get_confirmed_user_returns_user() -> None:
    request = Request(headers={"Authorization": "Bearer test-token"})
    user = create_confirmed_user(id=UUID("6d9c79d6-9641-4746-92d9-2cc9ebdca941"))
    crud = UserCRUD(existing_user=user)

    async def read_token(_: str) -> dict[str, str]:
        return {
            "sub": "6d9c79d6-9641-4746-92d9-2cc9ebdca941",
            "type": "access",
        }

    confirmed_user = await get_confirmed_user(request, read_token, crud)

    assert confirmed_user == user


@pytest.mark.anyio()
async def test_get_confirmed_user_raises_exception_if_request_is_missing() -> None:
    request = None
    crud = UserCRUD()

    async def read_token(_: str) -> dict[str, str]:
        return {
            "sub": "6d9c79d6-9641-4746-92d9-2cc9ebdca941",
            "type": "access",
        }

    with pytest.raises(UnauthorizedError, match="Authentication token required"):
        await get_confirmed_user(request, read_token, crud)


@pytest.mark.anyio()
async def test_get_confirmed_user_raises_exception_if_token_is_missing() -> None:
    request = Request(headers={})
    crud = UserCRUD()

    async def read_token(_: str) -> dict[str, str]:
        return {
            "sub": "6d9c79d6-9641-4746-92d9-2cc9ebdca941",
            "type": "access",
        }

    with pytest.raises(UnauthorizedError, match="Authentication token required"):
        await get_confirmed_user(request, read_token, crud)


@pytest.mark.anyio()
async def test_get_confirmed_user_raises_exception_if_token_is_invalid() -> None:
    request = Request(headers={"Authorization": "Bearer test-token"})
    crud = UserCRUD()

    async def read_token(_: str) -> dict[str, str]:
        raise InvalidTokenError

    with pytest.raises(UnauthorizedError, match="Invalid token"):
        await get_confirmed_user(request, read_token, crud)


@pytest.mark.anyio()
async def test_get_confirmed_user_raises_exception_if_token_has_invalid_type() -> None:
    request = Request(headers={"Authorization": "Bearer test-token"})
    crud = UserCRUD()

    async def read_token(_: str) -> dict[str, str]:
        return {
            "sub": "6d9c79d6-9641-4746-92d9-2cc9ebdca941",
            "type": "invalid-type",
        }

    with pytest.raises(UnauthorizedError, match="Invalid token"):
        await get_confirmed_user(request, read_token, crud)


@pytest.mark.anyio()
async def test_get_confirmed_raises_exception_if_user_is_not_found() -> None:
    request = Request(headers={"Authorization": "Bearer test-token"})
    crud = UserCRUD()

    async def read_token(_: str) -> dict[str, str]:
        return {
            "sub": "6d9c79d6-9641-4746-92d9-2cc9ebdca941",
            "type": "access",
        }

    with pytest.raises(UnauthorizedError, match="Invalid token"):
        await get_confirmed_user(request, read_token, crud)


@pytest.mark.anyio()
async def test_get_confirmed_user_raises_exception_if_user_email_is_not_confirmed() -> None:
    request = Request(headers={"Authorization": "Bearer test-token"})
    crud = UserCRUD(
        existing_user=create_user(id=UUID("6d9c79d6-9641-4746-92d9-2cc9ebdca941"))
    )

    async def read_token(_: str) -> dict[str, str]:
        return {
            "sub": "6d9c79d6-9641-4746-92d9-2cc9ebdca941",
            "type": "access",
        }

    with pytest.raises(UnauthorizedError, match="Invalid token"):
        await get_confirmed_user(request, read_token, crud)
