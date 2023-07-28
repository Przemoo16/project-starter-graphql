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
    schema: UserCreateSchema,
    password_hasher: PasswordHasher,
    crud: UserCRUDProtocol,
    success_callback: Callable[[User], None] = lambda _: None,
) -> User:
    try:
        await crud.read_one(UserFilters(email=schema.email))
    except NoObjectFoundError:
        create_data = UserCreateData(
            email=schema.email,
            hashed_password=password_hasher(schema.password.get_secret_value()),
        )
        user = await crud.create_and_refresh(create_data)
        success_callback(user)
        return user
    logger.info("User %r already exists", schema.email)
    raise UserAlreadyExistsError


async def update_user(
    user: User,
    schema: UserUpdateSchema,
    crud: UserCRUDProtocol,
    email_update_callback: Callable[[User], None] = lambda _: None,
) -> User:
    update_data = UserUpdateData.model_validate(schema.model_dump(exclude_unset=True))
    email_updated = False
    if update_data.email and update_data.email != user.email:
        try:
            await crud.read_one(UserFilters(email=schema.email))
        except NoObjectFoundError:
            update_data.confirmed_email = False
            email_updated = True
            logger.info("Marked the user %r as unconfirmed", user.email)
        else:
            logger.info("User %r already exists", schema.email)
            raise UserAlreadyExistsError
    updated_user = await crud.update_and_refresh(user, update_data)
    if email_updated:
        email_update_callback(updated_user)
        logger.info("Called the email update callback")
    return updated_user


async def delete_user(user: User, crud: UserCRUDProtocol) -> None:
    await crud.delete(user)
