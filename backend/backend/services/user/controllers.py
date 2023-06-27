from collections.abc import Callable
from copy import copy

from backend.libs.db.crud import CRUDProtocol, NoObjectFoundError
from backend.libs.email.message import HTMLMessage
from backend.services.user.exceptions import (
    InactiveUserError,
    UserAlreadyExistsError,
    UserNotFoundError,
)
from backend.services.user.models import User
from backend.services.user.schemas import UserCreateData, UserFilters, UserUpdateData

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
        raise InactiveUserError
    return user


async def update_user(user: User, data: UserUpdateData, crud: UserCRUDProtocol) -> User:
    if data.email and data.email != user.email:
        try:
            await get_user(UserFilters(email=data.email), crud)
        except UserNotFoundError:
            data = copy(data)
            data.confirmed_email = False
        else:
            raise UserAlreadyExistsError
    return await crud.update_and_refresh(user, data)


async def delete_user(user: User, crud: UserCRUDProtocol) -> None:
    await crud.delete(user)


def send_confirmation_email(
    url_template: str, token: str, send_email_func: Callable[[HTMLMessage], None]
) -> None:
    link = url_template.format(token=token)
    subject = "Confirm email"
    html_message = f"""
        <!DOCTYPE html>
        <html>
        <head></head>
        <body>
            <p>
            <a href="{link}">Click here to confirm your email</a>
            </p>
        </body>
        </html>
    """
    plain_message = f"Click the link to confirm your email: {link})"
    send_email_func(
        HTMLMessage(
            subject=subject, html_message=html_message, plain_message=plain_message
        )
    )
