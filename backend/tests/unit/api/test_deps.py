from dataclasses import dataclass
from uuid import UUID

import pytest

from backend.api.deps import UnauthorizedError, get_confirmed_user
from tests.unit.helpers.user import UserCRUD, create_confirmed_user, create_user


@dataclass
class Request:
    headers: dict[str, str]


@pytest.mark.anyio()
async def test_get_confirmed_user() -> None:
    request = Request(headers={"Authorization": "Bearer test-token"})
    user = create_confirmed_user(id=UUID("6d9c79d6-9641-4746-92d9-2cc9ebdca941"))
    crud = UserCRUD(existing_user=user)

    def read_token(_: str) -> dict[str, str]:
        return {
            "sub": "6d9c79d6-9641-4746-92d9-2cc9ebdca941",
            "type": "access",
        }

    confirmed_user = await get_confirmed_user(request, read_token, crud)

    assert confirmed_user == user


@pytest.mark.anyio()
async def test_get_confirmed_user_no_request() -> None:
    request = None
    crud = UserCRUD()

    def read_token(_: str) -> dict[str, str]:
        return {
            "sub": "6d9c79d6-9641-4746-92d9-2cc9ebdca941",
            "type": "access",
        }

    with pytest.raises(UnauthorizedError, match="Authentication token required"):
        await get_confirmed_user(request, read_token, crud)


@pytest.mark.anyio()
async def test_get_confirmed_user_no_bearer_token() -> None:
    request = Request(headers={})
    crud = UserCRUD()

    def read_token(_: str) -> dict[str, str]:
        return {
            "sub": "6d9c79d6-9641-4746-92d9-2cc9ebdca941",
            "type": "access",
        }

    with pytest.raises(UnauthorizedError, match="Authentication token required"):
        await get_confirmed_user(request, read_token, crud)


@pytest.mark.anyio()
async def test_get_confirmed_user_invalid_access_token() -> None:
    request = Request(headers={"Authorization": "Bearer test-token"})
    crud = UserCRUD()

    def read_token(_: str) -> dict[str, str]:
        return {
            "sub": "6d9c79d6-9641-4746-92d9-2cc9ebdca941",
            "type": "invalid-token",
        }

    with pytest.raises(UnauthorizedError, match="Invalid access token"):
        await get_confirmed_user(request, read_token, crud)


@pytest.mark.anyio()
async def test_get_confirmed_user_not_found() -> None:
    request = Request(headers={"Authorization": "Bearer test-token"})
    crud = UserCRUD()

    def read_token(_: str) -> dict[str, str]:
        return {
            "sub": "6d9c79d6-9641-4746-92d9-2cc9ebdca941",
            "type": "access",
        }

    with pytest.raises(UnauthorizedError, match="User not found"):
        await get_confirmed_user(request, read_token, crud)


@pytest.mark.anyio()
async def test_get_confirmed_user_not_confirmed() -> None:
    request = Request(headers={"Authorization": "Bearer test-token"})
    crud = UserCRUD(
        existing_user=create_user(id=UUID("6d9c79d6-9641-4746-92d9-2cc9ebdca941"))
    )

    def read_token(_: str) -> dict[str, str]:
        return {
            "sub": "6d9c79d6-9641-4746-92d9-2cc9ebdca941",
            "type": "access",
        }

    with pytest.raises(UnauthorizedError, match="User not confirmed"):
        await get_confirmed_user(request, read_token, crud)
