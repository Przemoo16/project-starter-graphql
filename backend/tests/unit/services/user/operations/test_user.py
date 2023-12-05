from contextlib import suppress

import pytest

from backend.services.user.exceptions import (
    UserAlreadyExistsError,
)
from backend.services.user.models import User
from backend.services.user.operations.user import create_user, delete_user, update_user
from backend.services.user.schemas import UserCreateSchema, UserUpdateSchema
from tests.unit.helpers.user import UserCRUD
from tests.unit.helpers.user import create_user as create_user_helper


async def hash_test_password(_: str) -> str:
    return "hashed_password"


@pytest.mark.anyio()
async def test_create_user_creates_user() -> None:
    data = UserCreateSchema(
        email="test@email.com", password="plain_password", full_name="Test User"
    )
    crud = UserCRUD()

    async def hash_password(_: str) -> str:
        return "hashed_password"

    user = await create_user(data, hash_password, crud)

    assert user.email == "test@email.com"
    assert user.hashed_password == "hashed_password"
    assert user.full_name == "Test User"


@pytest.mark.anyio()
async def test_create_user_raises_exception_if_user_already_exists() -> None:
    data = UserCreateSchema(
        email="test@email.com", password="plain_password", full_name="Test User"
    )
    crud = UserCRUD(existing_user=create_user_helper(email="test@email.com"))

    with pytest.raises(UserAlreadyExistsError):
        await create_user(data, hash_test_password, crud)


@pytest.mark.anyio()
async def test_create_user_calls_success_callback() -> None:
    data = UserCreateSchema(
        email="test@email.com", password="plain_password", full_name="Test User"
    )
    crud = UserCRUD()
    callback_called = False

    def callback(_: User) -> None:
        nonlocal callback_called
        callback_called = True

    await create_user(data, hash_test_password, crud, callback)

    assert callback_called


@pytest.mark.anyio()
async def test_create_user_does_not_call_success_callback_if_user_already_exists() -> None:
    data = UserCreateSchema(
        email="test@email.com", password="plain_password", full_name="Test User"
    )
    crud = UserCRUD(existing_user=create_user_helper(email="test@email.com"))
    callback_called = False

    def callback(_: User) -> None:
        nonlocal callback_called
        callback_called = True

    with suppress(UserAlreadyExistsError):
        await create_user(data, hash_test_password, crud, callback)

    assert not callback_called


@pytest.mark.anyio()
async def test_update_user_updates_user() -> None:
    data = UserUpdateSchema(full_name="Updated User")
    user = create_user_helper(full_name="Test User")
    crud = UserCRUD()

    updated_user = await update_user(user, data, crud)

    assert updated_user.full_name == "Updated User"


@pytest.mark.anyio()
async def test_delete_user_deletes_user() -> None:
    user = create_user_helper()
    crud = UserCRUD()

    await delete_user(user, crud)
