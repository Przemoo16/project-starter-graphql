import logging
from functools import partial
from typing import Annotated

from pydantic import ValidationError
from strawberry import argument

from backend.config.settings import get_settings
from backend.libs.api.context import Info
from backend.libs.api.types import from_pydantic_error
from backend.libs.db.crud import CRUD
from backend.libs.security.password import hash_password, verify_and_update_password
from backend.libs.security.token import (
    create_paseto_token_public_v4,
    read_paseto_token_public_v4,
)
from backend.services.user.controllers.auth import (
    create_access_token,
    create_refresh_token,
    login,
)
from backend.services.user.controllers.email import confirm_email
from backend.services.user.controllers.password import set_password
from backend.services.user.controllers.user import (
    create_user,
    get_confirmed_user,
)
from backend.services.user.exceptions import (
    InvalidCredentialsError,
    InvalidEmailConfirmationTokenError,
    InvalidResetPasswordTokenError,
    UserAlreadyConfirmedError,
    UserAlreadyExistsError,
    UserNotConfirmedError,
    UserNotFoundError,
)
from backend.services.user.models import User
from backend.services.user.schemas import (
    Credentials,
    SetPasswordData,
    UserCreateData,
    UserFilters,
    UserUpdateData,
)
from backend.services.user.tasks import (
    send_confirmation_email_task,
    send_reset_password_email_task,
)
from backend.services.user.types import (
    ConfirmEmailFailure,
    ConfirmEmailResponse,
    ConfirmEmailSuccess,
    CreateUserFailure,
    CreateUserResponse,
    CreateUserSuccess,
    InvalidCredentials,
    InvalidEmailConfirmationToken,
    InvalidResetPasswordToken,
    LoginFailure,
    LoginInput,
    LoginResponse,
    LoginSuccess,
    ResetPasswordResponse,
    SetPasswordFailure,
    SetPasswordInput,
    SetPasswordResponse,
    SetPasswordSuccess,
    UserAlreadyConfirmed,
    UserAlreadyExists,
    UserCreateInput,
    UserNotConfirmed,
)

logger = logging.getLogger(__name__)

UserCRUD = CRUD[User, UserCreateData, UserUpdateData, UserFilters]

user_settings = get_settings().user


async def create_user_resolver(
    info: Info, user_input: Annotated[UserCreateInput, argument(name="input")]
) -> CreateUserResponse:
    try:
        user_data = UserCreateData(
            email=user_input.email,
            password=user_input.password,
            password_hasher=hash_password,
        )
    except ValidationError as exc:
        return CreateUserFailure(problems=from_pydantic_error(exc))
    crud = UserCRUD(model=User, session=info.context.session)
    try:
        created_user = await create_user(user_data, crud)
    except UserAlreadyExistsError:
        return CreateUserFailure(problems=[UserAlreadyExists(email=user_input.email)])
    send_confirmation_email_task.delay(
        user_id=created_user.id, user_email=created_user.email
    )
    return CreateUserSuccess(id=created_user.id, email=created_user.email)


async def confirm_email_resolver(info: Info, token: str) -> ConfirmEmailResponse:
    crud = UserCRUD(model=User, session=info.context.session)
    try:
        user = await confirm_email(
            token,
            partial(read_paseto_token_public_v4, key=user_settings.auth_public_key),
            crud,
        )
    except InvalidEmailConfirmationTokenError:
        return ConfirmEmailFailure(problems=[InvalidEmailConfirmationToken()])
    except UserAlreadyConfirmedError as exc:
        return ConfirmEmailFailure(problems=[UserAlreadyConfirmed(email=exc.email)])
    return ConfirmEmailSuccess(id=user.id, email=user.email)


async def login_resolver(
    info: Info, credentials_input: Annotated[LoginInput, argument(name="input")]
) -> LoginResponse:
    crud = UserCRUD(model=User, session=info.context.session)
    credentials = Credentials(
        email=credentials_input.username, password=credentials_input.password
    )
    try:
        user = await login(credentials, verify_and_update_password, hash_password, crud)
    except InvalidCredentialsError:
        return LoginFailure(
            problems=[InvalidCredentials(username=credentials_input.username)]
        )
    except UserNotConfirmedError:
        return LoginFailure(
            problems=[UserNotConfirmed(email=credentials_input.username)]
        )
    return LoginSuccess(
        access_token=create_access_token(
            user_id=user.id,
            token_creator=partial(
                create_paseto_token_public_v4,
                expiration=int(user_settings.access_token_lifetime.total_seconds()),
                key=user_settings.auth_private_key.get_secret_value(),
            ),
        ),
        refresh_token=create_refresh_token(
            user_id=user.id,
            token_creator=partial(
                create_paseto_token_public_v4,
                expiration=int(user_settings.refresh_token_lifetime.total_seconds()),
                key=user_settings.auth_private_key.get_secret_value(),
            ),
        ),
        token_type="Bearer",  # nosec
    )


async def reset_password_resolver(info: Info, email: str) -> ResetPasswordResponse:
    crud = UserCRUD(model=User, session=info.context.session)
    try:
        user = await get_confirmed_user(UserFilters(email=email), crud)
    except UserNotFoundError:
        logger.debug("Message has not been sent because user not found")
    except UserNotConfirmedError:
        logger.debug("Message has not been sent because user not confirmed")
    else:
        send_reset_password_email_task.delay(
            user_id=user.id, user_email=user.email, user_password=user.hashed_password
        )
    return ResetPasswordResponse(email=email)


async def set_password_resolver(
    info: Info, set_password_input: Annotated[SetPasswordInput, argument(name="input")]
) -> SetPasswordResponse:
    try:
        set_password_data = SetPasswordData(
            token=set_password_input.token,
            password=set_password_input.password,
            password_hasher=hash_password,
        )
    except ValidationError as exc:
        return SetPasswordFailure(problems=from_pydantic_error(exc))
    crud = UserCRUD(model=User, session=info.context.session)
    try:
        await set_password(
            set_password_data,
            partial(read_paseto_token_public_v4, key=user_settings.auth_public_key),
            verify_and_update_password,
            crud,
        )
    except InvalidResetPasswordTokenError:
        return SetPasswordFailure(problems=[InvalidResetPasswordToken()])
    return SetPasswordSuccess()
