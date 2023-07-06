import logging
from collections.abc import Callable, Mapping
from copy import copy
from dataclasses import dataclass
from datetime import datetime
from enum import Enum, unique
from gettext import gettext as _
from typing import Any, Protocol
from uuid import UUID

from backend.libs.db.crud import CRUDProtocol, NoObjectFoundError
from backend.libs.email.message import HTMLMessage
from backend.libs.security.token import InvalidTokenError
from backend.services.user.exceptions import (
    InvalidCredentialsError,
    InvalidEmailConfirmationTokenError,
    UserAlreadyConfirmedError,
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

logger = logging.getLogger(__name__)

UserCRUDProtocol = CRUDProtocol[User, UserCreateData, UserUpdateData, UserFilters]
PasswordValidator = Callable[[str, str], tuple[bool, str | None]]
PasswordHasher = Callable[[str], str]


async def create_user(data: UserCreateData, crud: UserCRUDProtocol) -> User:
    try:
        await crud.read_one(UserFilters(email=data.email))
    except NoObjectFoundError:
        return await crud.create_and_refresh(data)
    raise UserAlreadyExistsError


async def get_user(filters: UserFilters, crud: UserCRUDProtocol) -> User:
    try:
        return await crud.read_one(filters)
    except NoObjectFoundError as exc:
        raise UserNotFoundError from exc


async def get_confirmed_user(filters: UserFilters, crud: UserCRUDProtocol) -> User:
    try:
        user = await crud.read_one(filters)
    except NoObjectFoundError as exc:
        raise UserNotFoundError from exc
    if not user.confirmed_email:
        raise UserNotConfirmedError
    return user


async def update_user(user: User, data: UserUpdateData, crud: UserCRUDProtocol) -> User:
    if data.email and data.email != user.email:
        try:
            await crud.read_one(UserFilters(email=data.email))
        except NoObjectFoundError:
            data = copy(data)
            data.confirmed_email = False
            logger.info("Mark the user %r as unconfirmed email", user.email)
            # TODO: Send email to confirm new email
        else:
            raise UserAlreadyExistsError
    return await crud.update_and_refresh(user, data)


async def delete_user(user: User, crud: UserCRUDProtocol) -> None:
    await crud.delete(user)


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


TokenCreator = Callable[[Mapping[str, Any]], str]
TokenReader = Callable[[str], dict[str, Any]]


@unique
class TokenType(Enum):
    EMAIL_CONFIRMATION = "email-confirmation"
    ACCESS = "access"
    REFRESH = "refresh"
    RESET_PASSWORD = "reset-password"  # nosec


@dataclass
class ConfirmationEmailTokenData:
    id: UUID
    email: str


def create_email_confirmation_token(
    user_id: UUID, user_email: str, token_creator: TokenCreator
) -> str:
    return token_creator(
        {
            "sub": str(user_id),
            "email": user_email,
            "type": TokenType.EMAIL_CONFIRMATION.value,
        }
    )


def read_email_confirmation_token(
    token: str, token_reader: TokenReader
) -> ConfirmationEmailTokenData:
    try:
        data = token_reader(token)
    except InvalidTokenError as exc:
        logger.debug("The %r token is invalid", token)
        raise InvalidEmailConfirmationTokenError from exc
    if data["type"] != TokenType.EMAIL_CONFIRMATION.value:
        logger.debug(
            "The %r token is not an email confirmation token, actual type: %r",
            token,
            data["type"],
        )
        raise InvalidEmailConfirmationTokenError
    return ConfirmationEmailTokenData(id=UUID(data["sub"]), email=data["email"])


async def confirm_email(
    token: str, token_reader: TokenReader, crud: UserCRUDProtocol
) -> User:
    data = read_email_confirmation_token(token, token_reader)
    try:
        user = await crud.read_one(UserFilters(id=data.id, email=data.email))
    except NoObjectFoundError as exc:
        raise InvalidEmailConfirmationTokenError from exc
    if user.confirmed_email:
        raise UserAlreadyConfirmedError(email=user.email)
    return await crud.update_and_refresh(user, UserUpdateData(confirmed_email=True))


async def authenticate(
    credentials: Credentials,
    password_validator: PasswordValidator,
    password_hasher: PasswordHasher,
    crud: UserCRUDProtocol,
) -> User:
    try:
        user = await crud.read_one(UserFilters(email=credentials.email))
    except NoObjectFoundError as exc:
        # Run the password hasher to mitigate timing attack
        password_hasher(credentials.password)
        logger.debug("User %r not found", credentials.email)
        raise InvalidCredentialsError from exc
    is_valid, updated_password_hash = password_validator(
        credentials.password, user.hashed_password
    )
    if not is_valid:
        logger.debug("Invalid password for the user %r", user.email)
        raise InvalidCredentialsError
    if not user.confirmed_email:
        raise UserNotConfirmedError
    if updated_password_hash:
        user = await crud.update_and_refresh(
            user, UserUpdateData(hashed_password=updated_password_hash)
        )
        logger.info("Updated password hash for the user %r", user.email)
    return user


async def login(
    credentials: Credentials,
    password_validator: PasswordValidator,
    password_hasher: PasswordHasher,
    crud: UserCRUDProtocol,
) -> User:
    user = await authenticate(credentials, password_validator, password_hasher, crud)
    return await crud.update_and_refresh(
        user, UserUpdateData(last_login=datetime.utcnow())
    )


def create_access_token(user_id: UUID, token_creator: TokenCreator) -> str:
    return token_creator({"sub": str(user_id), "type": TokenType.ACCESS.value})


def create_refresh_token(user_id: UUID, token_creator: TokenCreator) -> str:
    return token_creator({"sub": str(user_id), "type": TokenType.REFRESH.value})


def send_reset_password_email(
    url_template: str,
    token: str,
    template_loader: TemplateLoader,
    send_email_func: Callable[[HTMLMessage], None],
) -> None:
    link = url_template.format(token=token)
    subject = _("Reset password")
    html_message = template_loader("reset-password.html", link=link)
    plain_message = _("Click the link to reset your password: {link}").format(link=link)
    send_email_func(
        HTMLMessage(
            subject=subject, html_message=html_message, plain_message=plain_message
        )
    )


def create_reset_password_token(
    user_id: UUID,
    user_password: str,
    password_hasher: PasswordHasher,
    token_creator: TokenCreator,
) -> str:
    return token_creator(
        {
            "sub": str(user_id),
            "fingerprint": password_hasher(user_password),
            "type": TokenType.RESET_PASSWORD.value,
        }
    )
