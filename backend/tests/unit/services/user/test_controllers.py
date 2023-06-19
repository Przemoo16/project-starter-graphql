import pytest

from backend.libs.db.crud import NoObjectFoundError
from backend.models.user import User
from backend.services.user.controllers import (
    create_user,
    delete_user,
    get_active_user,
    get_user,
    update_user,
)
from backend.services.user.exceptions import (
    InactiveUserError,
    UserAlreadyExistsError,
    UserNotFoundError,
)
from backend.services.user.schemas import UserCreateData, UserFilters, UserUpdateData
from tests.unit.stubs.crud.base import CRUDStub


class TestUserCRUD(  # pylint: disable=abstract-method
    CRUDStub[User, UserCreateData, UserUpdateData, UserFilters]
):
    def __init__(self, existing_user: User | None = None):
        self.existing_user = existing_user

    async def create_and_refresh(self, data: UserCreateData) -> User:
        return User(
            email=data.email,
            hashed_password=data.hashed_password,
        )

    async def read_one(self, filters: UserFilters) -> User:
        if self.existing_user:
            return self.existing_user
        raise NoObjectFoundError

    async def update_and_refresh(self, obj: User, data: UserUpdateData) -> User:
        return User(
            email=data.email,
            hashed_password=data.hashed_password,
            confirmed_email=data.confirmed_email,
        )

    async def delete(self, obj: User) -> None:
        pass


@pytest.mark.anyio()
async def test_create_user() -> None:
    data = UserCreateData(
        email="test@email.com",
        password="plain_password",
        hash_password_algorithm=lambda _: "hashed_password",
    )
    crud = TestUserCRUD()

    user = await create_user(data, crud)

    assert user.email == "test@email.com"


@pytest.mark.anyio()
async def test_create_user_already_exists() -> None:
    data = UserCreateData(
        email="test@email.com",
        password="plain_password",
        hash_password_algorithm=lambda _: "hashed_password",
    )
    crud = TestUserCRUD(existing_user=User(email="test@email.com"))

    with pytest.raises(UserAlreadyExistsError):
        await create_user(data, crud)


@pytest.mark.anyio()
async def test_get_user() -> None:
    filters = UserFilters(email="test@email.com")
    crud = TestUserCRUD(existing_user=User(email="test@email.com"))

    user = await get_user(filters, crud)

    assert user


@pytest.mark.anyio()
async def test_get_user_not_found() -> None:
    filters = UserFilters(email="test@email.com")
    crud = TestUserCRUD()

    with pytest.raises(UserNotFoundError):
        await get_user(filters, crud)


@pytest.mark.anyio()
async def test_get_active_user() -> None:
    filters = UserFilters(email="test@email.com")
    crud = TestUserCRUD(
        existing_user=User(email="test@email.com", confirmed_email=True)
    )

    user = await get_active_user(filters, crud)

    assert user


@pytest.mark.anyio()
async def test_get_inactive_user() -> None:
    filters = UserFilters(email="test@email.com")
    crud = TestUserCRUD(
        existing_user=User(email="test@email.com", confirmed_email=False)
    )

    with pytest.raises(InactiveUserError):
        await get_active_user(filters, crud)


@pytest.mark.anyio()
async def test_update_user() -> None:
    data = UserUpdateData(confirmed_email=True)
    user = User(confirmed_email=False)
    crud = TestUserCRUD()

    updated_user = await update_user(user, data, crud)

    assert updated_user.confirmed_email is True


@pytest.mark.anyio()
async def test_update_user_email() -> None:
    data = UserUpdateData(email="updated@email.com")
    user = User(email="test@email.com")
    crud = TestUserCRUD()

    updated_user = await update_user(user, data, crud)

    assert updated_user.email == "updated@email.com"
    assert updated_user.confirmed_email is False


@pytest.mark.anyio()
async def test_update_user_email_the_same_email_provided() -> None:
    data = UserUpdateData(email="test@email.com")
    user = User(email="test@email.com")
    crud = TestUserCRUD()

    updated_user = await update_user(user, data, crud)

    assert updated_user.email == "test@email.com"
    assert updated_user.confirmed_email is not False


@pytest.mark.anyio()
async def test_update_user_email_already_exists() -> None:
    data = UserUpdateData(email="updated@email.com")
    user = User(email="test@email.com")
    crud = TestUserCRUD(existing_user=User(email="updated@email.com"))

    with pytest.raises(UserAlreadyExistsError):
        await update_user(user, data, crud)


@pytest.mark.anyio()
async def test_delete_user() -> None:
    user = User()
    crud = TestUserCRUD()

    await delete_user(user, crud)
