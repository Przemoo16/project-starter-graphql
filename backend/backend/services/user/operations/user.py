import logging
from collections.abc import Callable

from backend.libs.db.crud import NoObjectFoundError
from backend.services.user.crud import (
    UserCreateData,
    UserCRUDProtocol,
    UserFilters,
    UserUpdateData,
)
from backend.services.user.exceptions import UserAlreadyExistsError
from backend.services.user.models import User
from backend.services.user.schemas import UserCreateSchema, UserUpdateSchema

logger = logging.getLogger(__name__)

PasswordHasher = Callable[[str], str]


async def create_user(
    data: UserCreateSchema,
    password_hasher: PasswordHasher,
    crud: UserCRUDProtocol,
    success_callback: Callable[[User], None] = lambda _: None,
) -> User:
    try:
        await crud.read_one(UserFilters(email=data.email))
    except NoObjectFoundError:
        create_data = UserCreateData(
            **data.model_dump(),
            hashed_password=password_hasher(data.password.get_secret_value()),
        )
        user = await crud.create_and_refresh(create_data)
        success_callback(user)
        return user
    logger.info("User %r already exists", data.email)
    raise UserAlreadyExistsError


async def update_user(
    user: User, data: UserUpdateSchema, crud: UserCRUDProtocol
) -> User:
    update_data = UserUpdateData.model_validate(data.model_dump(exclude_unset=True))
    return await crud.update_and_refresh(user, update_data)


async def delete_user(user: User, crud: UserCRUDProtocol) -> None:
    await crud.delete(user)
