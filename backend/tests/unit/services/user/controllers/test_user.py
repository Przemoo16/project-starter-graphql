import pytest

from backend.services.user.controllers.user import (
    create_user,
    delete_user,
    get_confirmed_user,
    get_user,
    update_user,
)
from backend.services.user.exceptions import (
    UserAlreadyExistsError,
    UserNotConfirmedError,
    UserNotFoundError,
)
from backend.services.user.schemas import (
    UserCreateData,
    UserFilters,
    UserUpdateData,
)
from tests.unit.helpers.user import UserCRUD
from tests.unit.helpers.user import (
    create_confirmed_user as create_confirmed_user_helper,
)
from tests.unit.helpers.user import create_user as create_user_helper


def get_test_password(_: str) -> str:
    return "hashed_password"


@pytest.mark.anyio()
async def test_create_user() -> None:
    data = UserCreateData(
        email="test@email.com",
        password="plain_password",
        password_hasher=get_test_password,
    )
    crud = UserCRUD()

    user = await create_user(data, crud)

    assert user.email == "test@email.com"


@pytest.mark.anyio()
async def test_create_user_already_exists() -> None:
    data = UserCreateData(
        email="test@email.com",
        password="plain_password",
        password_hasher=get_test_password,
    )
    crud = UserCRUD(existing_user=create_user_helper(email="test@email.com"))

    with pytest.raises(UserAlreadyExistsError):
        await create_user(data, crud)


@pytest.mark.anyio()
async def test_get_user() -> None:
    filters = UserFilters(email="test@email.com")
    crud = UserCRUD(existing_user=create_user_helper(email="test@email.com"))

    user = await get_user(filters, crud)

    assert user


@pytest.mark.anyio()
async def test_get_user_not_found() -> None:
    filters = UserFilters(email="test@email.com")
    crud = UserCRUD()

    with pytest.raises(UserNotFoundError):
        await get_user(filters, crud)


@pytest.mark.anyio()
async def test_get_confirmed_user() -> None:
    filters = UserFilters(email="test@email.com")
    crud = UserCRUD(existing_user=create_confirmed_user_helper(email="test@email.com"))

    user = await get_confirmed_user(filters, crud)

    assert user


@pytest.mark.anyio()
async def test_get_confirmed_user_not_found() -> None:
    filters = UserFilters(email="test@email.com")
    crud = UserCRUD()

    with pytest.raises(UserNotFoundError):
        await get_confirmed_user(filters, crud)


@pytest.mark.anyio()
async def test_get_not_confirmed_user() -> None:
    filters = UserFilters(email="test@email.com")
    crud = UserCRUD(existing_user=create_user_helper(email="test@email.com"))

    with pytest.raises(UserNotConfirmedError):
        await get_confirmed_user(filters, crud)


@pytest.mark.anyio()
async def test_update_user() -> None:
    data = UserUpdateData(confirmed_email=True)
    user = create_user_helper(confirmed_email=False)
    crud = UserCRUD()

    updated_user = await update_user(user, data, crud)

    assert updated_user.confirmed_email is True


@pytest.mark.anyio()
async def test_update_user_email() -> None:
    data = UserUpdateData(email="updated@email.com")
    user = create_user_helper(email="test@email.com", confirmed_email=True)
    crud = UserCRUD()

    updated_user = await update_user(user, data, crud)

    assert updated_user.email == "updated@email.com"
    assert updated_user.confirmed_email is False


@pytest.mark.anyio()
async def test_update_user_email_the_same_email_provided() -> None:
    data = UserUpdateData(email="test@email.com")
    user = create_user_helper(email="test@email.com", confirmed_email=True)
    crud = UserCRUD()

    updated_user = await update_user(user, data, crud)

    assert updated_user.email == "test@email.com"
    assert updated_user.confirmed_email is not False


@pytest.mark.anyio()
async def test_update_user_email_already_exists() -> None:
    data = UserUpdateData(email="updated@email.com")
    user = create_user_helper(email="test@email.com")
    crud = UserCRUD(existing_user=create_user_helper(email="updated@email.com"))

    with pytest.raises(UserAlreadyExistsError):
        await update_user(user, data, crud)


@pytest.mark.anyio()
async def test_delete_user() -> None:
    user = create_user_helper()
    crud = UserCRUD()

    await delete_user(user, crud)
