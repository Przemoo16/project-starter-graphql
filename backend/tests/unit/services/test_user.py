import pytest

from backend.models.user import User
from backend.services.user import create_user
from backend.types.user import UserCreate, UserFilters, UserUpdate
from tests.unit.stubs.crud.base import CRUDStub


class TestUserCRUD(  # pylint: disable=abstract-method
    CRUDStub[User, UserCreate, UserUpdate, UserFilters]
):
    async def create_and_refresh(self, data: UserCreate) -> User:
        return User(email=data.email, password=data.password, full_name=data.full_name)


@pytest.mark.anyio()
async def test_create_user() -> None:
    data = UserCreate(
        email="test@email.com", password="plain_password", full_name="Test User"
    )

    user = await create_user(data, TestUserCRUD())

    assert user.email == "test@email.com"
    assert user.full_name == "Test User"
