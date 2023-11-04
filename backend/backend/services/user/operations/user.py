import logging
from collections.abc import Callable

from backend.libs.db.crud import NoObjectFoundError
from backend.services.user.crud import UserCreateData, UserFilters, UserUpdateData
from backend.services.user.exceptions import UserAlreadyExistsError
from backend.services.user.models import User
from backend.services.user.operations.types import AsyncPasswordHasher, UserCRUDProtocol
from backend.services.user.schemas import UserCreateSchema, UserUpdateSchema

_logger = logging.getLogger(__name__)


async def create_user(
    data: UserCreateSchema,
    password_hasher: AsyncPasswordHasher,
    crud: UserCRUDProtocol,
    success_callback: Callable[[User], None] = lambda _: None,
) -> User:
    try:
        await crud.read_one(UserFilters(email=data.email))
    except NoObjectFoundError:
        data_dict = data.model_dump(exclude={"password"})
        hashed_password = await password_hasher(data.password.get_secret_value())
        create_data = UserCreateData(**data_dict, hashed_password=hashed_password)
        user = await crud.create_and_refresh(create_data)
        success_callback(user)
        return user
    _logger.info("User %r already exists", data.email)
    raise UserAlreadyExistsError


async def update_user(
    user: User, data: UserUpdateSchema, crud: UserCRUDProtocol
) -> User:
    data_dict = data.model_dump(exclude_unset=True)
    update_data = UserUpdateData(**data_dict)
    return await crud.update_and_refresh(user, update_data)


async def delete_user(user: User, crud: UserCRUDProtocol) -> None:
    await crud.delete(user)
