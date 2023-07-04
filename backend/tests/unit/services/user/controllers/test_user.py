from contextlib import suppress

import pytest

from backend.libs.db.crud import NoObjectFoundError
from backend.services.user.controllers.user import (
    authenticate,
    create_user,
    delete_user,
    get_user,
    login_user,
    update_user,
)
from backend.services.user.exceptions import (
    InvalidCredentialsError,
    UserAlreadyExistsError,
    UserNotConfirmedError,
    UserNotFoundError,
)
from backend.services.user.models import User
from backend.services.user.schemas import (
    Credentials,
    UserCreateData,
    UserFilters,
    UserUpdateData,
)
from tests.unit.stubs.crud.base import CRUDStub


class UserCRUD(  # pylint: disable=abstract-method
    CRUDStub[User, UserCreateData, UserUpdateData, UserFilters]
):
    def __init__(self, existing_user: User | None = None):
        self.existing_user = existing_user

    async def create_and_refresh(self, data: UserCreateData) -> User:
        return User(**data.model_dump())

    async def read_one(self, filters: UserFilters) -> User:
        if self.existing_user:
            return self.existing_user
        raise NoObjectFoundError

    async def update_and_refresh(self, obj: User, data: UserUpdateData) -> User:
        return User(**data.model_dump(exclude_unset=True))

    async def delete(self, obj: User) -> None:
        pass


@pytest.mark.anyio()
async def test_create_user() -> None:
    data = UserCreateData(
        email="test@email.com",
        password="plain_password",
        password_hasher=lambda _: "hashed_password",
    )
    crud = UserCRUD()

    user = await create_user(data, crud)

    assert user.email == "test@email.com"


@pytest.mark.anyio()
async def test_create_user_already_exists() -> None:
    data = UserCreateData(
        email="test@email.com",
        password="plain_password",
        password_hasher=lambda _: "hashed_password",
    )
    crud = UserCRUD(existing_user=User(email="test@email.com"))

    with pytest.raises(UserAlreadyExistsError):
        await create_user(data, crud)


@pytest.mark.anyio()
async def test_get_user() -> None:
    filters = UserFilters(email="test@email.com")
    crud = UserCRUD(existing_user=User(email="test@email.com"))

    user = await get_user(filters, crud)

    assert user


@pytest.mark.anyio()
async def test_get_user_not_found() -> None:
    filters = UserFilters(email="test@email.com")
    crud = UserCRUD()

    with pytest.raises(UserNotFoundError):
        await get_user(filters, crud)


@pytest.mark.anyio()
async def test_update_user() -> None:
    data = UserUpdateData(confirmed_email=True)
    user = User(confirmed_email=False)
    crud = UserCRUD()

    updated_user = await update_user(user, data, crud)

    assert updated_user.confirmed_email is True


@pytest.mark.anyio()
async def test_update_user_email() -> None:
    data = UserUpdateData(email="updated@email.com")
    user = User(email="test@email.com")
    crud = UserCRUD()

    updated_user = await update_user(user, data, crud)

    assert updated_user.email == "updated@email.com"
    assert updated_user.confirmed_email is False


@pytest.mark.anyio()
async def test_update_user_email_the_same_email_provided() -> None:
    data = UserUpdateData(email="test@email.com")
    user = User(email="test@email.com")
    crud = UserCRUD()

    updated_user = await update_user(user, data, crud)

    assert updated_user.email == "test@email.com"
    assert updated_user.confirmed_email is not False


@pytest.mark.anyio()
async def test_update_user_email_already_exists() -> None:
    data = UserUpdateData(email="updated@email.com")
    user = User(email="test@email.com")
    crud = UserCRUD(existing_user=User(email="updated@email.com"))

    with pytest.raises(UserAlreadyExistsError):
        await update_user(user, data, crud)


@pytest.mark.anyio()
async def test_delete_user() -> None:
    user = User()
    crud = UserCRUD()

    await delete_user(user, crud)


def success_password_validator(*_: str) -> tuple[bool, None]:
    return True, None


@pytest.mark.anyio()
async def test_update_last_login_when_user_log_in() -> None:
    credentials = Credentials(email="test@email.com", password="plain_password")
    crud = UserCRUD(
        existing_user=User(
            email="test@email.com",
            hashed_password="hashed_password",
            confirmed_email=True,
            last_login=None,
        )
    )

    user = await login_user(
        credentials, success_password_validator, lambda _: "hashed_password", crud
    )

    assert user.last_login


@pytest.mark.anyio()
async def test_success_authentication_without_password_hash_update() -> None:
    credentials = Credentials(email="test@email.com", password="plain_password")
    crud = UserCRUD(
        existing_user=User(
            email="test@email.com",
            hashed_password="hashed_password",
            confirmed_email=True,
        )
    )

    user = await authenticate(
        credentials, success_password_validator, lambda _: "hashed_password", crud
    )

    assert user.hashed_password == "hashed_password"


@pytest.mark.anyio()
async def test_success_authentication_with_password_hash_update() -> None:
    credentials = Credentials(email="test@email.com", password="plain_password")
    crud = UserCRUD(
        existing_user=User(
            email="test@email.com",
            hashed_password="hashed_password",
            confirmed_email=True,
        )
    )

    def password_validator_update_hash(*_: str) -> tuple[bool, str]:
        return True, "new_hashed_password"

    user = await authenticate(
        credentials, password_validator_update_hash, lambda _: "hashed_password", crud
    )

    assert user.hashed_password == "new_hashed_password"


@pytest.mark.anyio()
async def test_failure_authentication_user_not_found() -> None:
    credentials = Credentials(email="test@email.com", password="plain_password")
    crud = UserCRUD()

    with pytest.raises(InvalidCredentialsError):
        await authenticate(
            credentials, success_password_validator, lambda _: "hashed_password", crud
        )


@pytest.mark.anyio()
@pytest.mark.parametrize(
    ("user", "hasher_called"),
    [
        (
            User(
                email="test@email.com",
                hashed_password="hashed_password",
                confirmed_email=True,
            ),
            False,
        ),
        (None, True),
    ],
)
async def test_authentication_calling_password_hasher(
    user: User | None, hasher_called: bool
) -> None:
    credentials = Credentials(email="test@email.com", password="plain_password")
    crud = UserCRUD(existing_user=user)

    hash_function_called = False

    def hash_func(_: str) -> str:
        nonlocal hash_function_called
        hash_function_called = True
        return "hashed_password"

    with suppress(InvalidCredentialsError):
        await authenticate(credentials, success_password_validator, hash_func, crud)

    assert hash_function_called == hasher_called


@pytest.mark.anyio()
async def test_failure_authentication_invalid_password() -> None:
    credentials = Credentials(email="test@email.com", password="plain_password")
    crud = UserCRUD(
        existing_user=User(
            email="test@email.com",
            hashed_password="hashed_password",
            confirmed_email=True,
        )
    )

    def failure_validator(*_: str) -> tuple[bool, None]:
        return False, None

    with pytest.raises(InvalidCredentialsError):
        await authenticate(
            credentials, failure_validator, lambda _: "hashed_password", crud
        )


@pytest.mark.anyio()
async def test_failure_authentication_user_not_confirmed() -> None:
    credentials = Credentials(email="test@email.com", password="plain_password")
    crud = UserCRUD(
        existing_user=User(
            email="test@email.com",
            hashed_password="hashed_password",
            confirmed_email=False,
        )
    )

    with pytest.raises(UserNotConfirmedError):
        await authenticate(
            credentials, success_password_validator, lambda _: "hashed_password", crud
        )
