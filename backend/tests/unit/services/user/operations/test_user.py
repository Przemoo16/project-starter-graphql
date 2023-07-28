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


def get_test_password(_: str) -> str:
    return "hashed_password"


@pytest.mark.anyio()
async def test_create_user() -> None:
    schema = UserCreateSchema(email="test@email.com", password="plain_password")
    crud = UserCRUD()

    def hash_password(_: str) -> str:
        return "hashed_password"

    user = await create_user(schema, hash_password, crud)

    assert user.email == "test@email.com"
    assert user.hashed_password == "hashed_password"


@pytest.mark.anyio()
async def test_create_user_already_exists() -> None:
    schema = UserCreateSchema(email="test@email.com", password="plain_password")
    crud = UserCRUD(existing_user=create_user_helper(email="test@email.com"))

    with pytest.raises(UserAlreadyExistsError):
        await create_user(schema, get_test_password, crud)


@pytest.mark.anyio()
async def test_create_user_callback_called() -> None:
    schema = UserCreateSchema(email="test@email.com", password="plain_password")
    crud = UserCRUD()
    callback_called = False

    def callback(_: User) -> None:
        nonlocal callback_called
        callback_called = True

    await create_user(schema, get_test_password, crud, callback)

    assert callback_called


@pytest.mark.anyio()
async def test_create_user_callback_not_called() -> None:
    schema = UserCreateSchema(email="test@email.com", password="plain_password")
    crud = UserCRUD(existing_user=create_user_helper(email="test@email.com"))
    callback_called = False

    def callback(_: User) -> None:
        nonlocal callback_called
        callback_called = True

    with suppress(UserAlreadyExistsError):
        await create_user(schema, get_test_password, crud, callback)

    assert not callback_called


@pytest.mark.anyio()
async def test_update_user_email() -> None:
    schema = UserUpdateSchema(email="updated@email.com")
    user = create_user_helper(email="test@email.com", confirmed_email=True)
    crud = UserCRUD()

    updated_user = await update_user(user, schema, crud)

    assert updated_user.email == "updated@email.com"
    assert updated_user.confirmed_email is False


@pytest.mark.anyio()
async def test_update_user_email_the_same_email_provided() -> None:
    schema = UserUpdateSchema(email="test@email.com")
    user = create_user_helper(email="test@email.com", confirmed_email=True)
    crud = UserCRUD()

    updated_user = await update_user(user, schema, crud)

    assert updated_user.email == "test@email.com"
    assert updated_user.confirmed_email is True


@pytest.mark.anyio()
async def test_update_user_email_already_exists() -> None:
    schema = UserUpdateSchema(email="updated@email.com")
    user = create_user_helper(email="test@email.com")
    crud = UserCRUD(existing_user=create_user_helper(email="updated@email.com"))

    with pytest.raises(UserAlreadyExistsError):
        await update_user(user, schema, crud)


@pytest.mark.anyio()
async def test_update_user_email_callback_called() -> None:
    schema = UserUpdateSchema(email="updated@email.com")
    user = create_user_helper(email="test@email.com")
    crud = UserCRUD()
    callback_called = False

    def callback(_: User) -> None:
        nonlocal callback_called
        callback_called = True

    await update_user(user, schema, crud, callback)

    assert callback_called


@pytest.mark.anyio()
async def test_update_user_email_callback_not_called() -> None:
    schema = UserUpdateSchema()
    user = create_user_helper()
    crud = UserCRUD()
    callback_called = False

    def callback(_: User) -> None:
        nonlocal callback_called
        callback_called = True

    await update_user(user, schema, crud, callback)

    assert not callback_called


@pytest.mark.anyio()
async def test_delete_user() -> None:
    user = create_user_helper()
    crud = UserCRUD()

    await delete_user(user, crud)
