import pytest

from backend.libs.db.crud import NoObjectFoundError
from backend.models.user import User
from backend.services.user import (
    InactiveUserError,
    UserAlreadyExistsError,
    UserNotFoundError,
    create_user,
    delete_user,
    get_active_user,
    get_user,
    update_user,
)
from backend.types.user import UserCreate, UserFilters, UserUpdate
from tests.unit.stubs.crud.base import CRUDStub


class TestUserCRUD(  # pylint: disable=abstract-method
    CRUDStub[User, UserCreate, UserUpdate, UserFilters]
):
    def __init__(self, existing_user: User | None = None):
        self.existing_user = existing_user

    async def create_and_refresh(self, data: UserCreate) -> User:
        return User(email=data.email, password=data.password, full_name=data.full_name)

    async def read_one(self, filters: UserFilters) -> User:
        if self.existing_user:
            return self.existing_user
        raise NoObjectFoundError

    async def update_and_refresh(self, obj: User, data: UserUpdate) -> User:
        return User(
            email=data.email,
            password=data.password,
            full_name=data.full_name,
            confirmed_email=data.confirmed_email,
        )

    async def delete(self, obj: User) -> None:
        pass


def hash_password(_: str) -> str:
    return "hashed_password"


@pytest.mark.anyio()
async def test_create_user() -> None:
    data = UserCreate(
        email="test@email.com", password="plain_password", full_name="Test User"
    )

    user = await create_user(data, TestUserCRUD())

    assert user.email == "test@email.com"
    assert user.full_name == "Test User"


@pytest.mark.anyio()
async def test_create_user_password_is_hashed() -> None:
    data = UserCreate(
        email="test@email.com", password="plain_password", full_name="Test User"
    )

    user = await create_user(data, TestUserCRUD())

    assert user.password != "plain_password"


@pytest.mark.anyio()
async def test_create_user_already_exists() -> None:
    data = UserCreate(
        email="test@email.com", password="plain_password", full_name="Test User"
    )

    with pytest.raises(UserAlreadyExistsError):
        await create_user(
            data, TestUserCRUD(existing_user=User(email="test@email.com"))
        )


@pytest.mark.anyio()
async def test_get_user() -> None:
    filters = UserFilters(email="test@email.com")

    user = await get_user(
        filters, TestUserCRUD(existing_user=User(email="test@email.com"))
    )

    assert user


@pytest.mark.anyio()
async def test_get_user_not_found() -> None:
    filters = UserFilters(email="test@email.com")

    with pytest.raises(UserNotFoundError):
        await get_user(filters, TestUserCRUD())


@pytest.mark.anyio()
async def test_get_active_user() -> None:
    filters = UserFilters(email="test@email.com")

    user = await get_active_user(
        filters,
        TestUserCRUD(existing_user=User(email="test@email.com", confirmed_email=True)),
    )

    assert user


@pytest.mark.anyio()
async def test_get_inactive_user() -> None:
    filters = UserFilters(email="test@email.com")

    with pytest.raises(InactiveUserError):
        await get_active_user(
            filters,
            TestUserCRUD(
                existing_user=User(email="test@email.com", confirmed_email=False)
            ),
        )


@pytest.mark.anyio()
async def test_update_user() -> None:
    data = UserUpdate(full_name="Updated User")

    user = await update_user(User(full_name="Test User"), data, TestUserCRUD())

    assert user.full_name == "Updated User"


@pytest.mark.anyio()
async def test_update_user_email() -> None:
    data = UserUpdate(email="updated@email.com")

    user = await update_user(
        User(email="test@email.com", confirmed_email=True), data, TestUserCRUD()
    )

    assert user.email == "updated@email.com"
    assert user.confirmed_email is False


@pytest.mark.anyio()
async def test_update_user_email_already_exists() -> None:
    data = UserUpdate(email="updated@email.com")

    with pytest.raises(UserAlreadyExistsError):
        await update_user(
            User(email="test@email.com"),
            data,
            TestUserCRUD(existing_user=User(email="updated@email.com")),
        )


@pytest.mark.anyio()
async def test_update_user_password_is_hashed() -> None:
    data = UserUpdate(password="new_password")

    user = await update_user(User(password="current_password"), data, TestUserCRUD())

    assert user.password != "current_password"
    assert user.password != "new_password"


@pytest.mark.anyio()
async def test_delete_user() -> None:
    await delete_user(User(), TestUserCRUD())
