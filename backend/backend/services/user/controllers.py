import logging
from collections.abc import Callable
from copy import copy
from gettext import gettext as _
from typing import Any, Protocol

from backend.libs.db.crud import CRUDProtocol, NoObjectFoundError
from backend.libs.email.message import HTMLMessage
from backend.services.user.exceptions import (
    InvalidCredentialsError,
    UserAlreadyExistsError,
    UserInactiveError,
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

logger = logging.getLogger(__name__)

UserCRUDProtocol = CRUDProtocol[User, UserCreateData, UserUpdateData, UserFilters]


async def create_user(data: UserCreateData, crud: UserCRUDProtocol) -> User:
    try:
        await get_user(UserFilters(email=data.email), crud)
    except UserNotFoundError:
        return await crud.create_and_refresh(data)
    raise UserAlreadyExistsError


async def get_user(filters: UserFilters, crud: UserCRUDProtocol) -> User:
    try:
        return await crud.read_one(filters)
    except NoObjectFoundError as exc:
        raise UserNotFoundError from exc


async def get_active_user(filters: UserFilters, crud: UserCRUDProtocol) -> User:
    user = await get_user(filters, crud)
    if not user.is_active:
        raise UserInactiveError
    return user


async def update_user(user: User, data: UserUpdateData, crud: UserCRUDProtocol) -> User:
    if data.email and data.email != user.email:
        try:
            await get_user(UserFilters(email=data.email), crud)
        except UserNotFoundError:
            data = copy(data)
            data.confirmed_email = False
            logger.info("Mark the user %r as unconfirmed email", user.email)
        else:
            raise UserAlreadyExistsError
    return await crud.update_and_refresh(user, data)


async def delete_user(user: User, crud: UserCRUDProtocol) -> None:
    await crud.delete(user)


async def authenticate(
    credentials: Credentials,
    password_validator: Callable[[str, str], tuple[bool, str | None]],
    password_hasher: Callable[[str], str],
    crud: UserCRUDProtocol,
) -> User:
    try:
        user = await get_user(UserFilters(email=credentials.email), crud)
    except UserNotFoundError as exc:
        # Run the password hasher to mitigate timing attack
        password_hasher(credentials.password)
        logger.info("User %r not found", credentials.email)
        raise InvalidCredentialsError from exc
    is_valid, updated_password_hash = password_validator(
        credentials.password, user.hashed_password
    )
    if not is_valid:
        logger.info("Invalid password for the user %r", user.email)
        raise InvalidCredentialsError
    if not user.confirmed_email:
        raise UserNotConfirmedError
    if updated_password_hash:
        user = await crud.update_and_refresh(
            user, UserUpdateData(hashed_password=updated_password_hash)
        )
        logger.info("Updated password hash for the user %r", user.email)
    return user


class TemplateLoader(Protocol):
    def __call__(self, name: str, **kwargs: Any) -> str:
        ...


def send_confirmation_email(
    url_template: str,
    token: str,
    template_loader: TemplateLoader,
    send_email_func: Callable[[HTMLMessage], None],
) -> None:
    link = url_template.format(token=token)
    subject = _("Confirm email")
    html_message = template_loader("email-confirmation.html", link=link)
    plain_message = _("Click the link to confirm your email: {link}").format(link=link)
    send_email_func(
        HTMLMessage(
            subject=subject, html_message=html_message, plain_message=plain_message
        )
    )
