import logging
from functools import partial
from typing import Annotated

from pydantic import ValidationError
from strawberry import argument

from backend.config.settings import get_settings
from backend.libs.api.context import Info
from backend.libs.api.types import from_pydantic_error
from backend.libs.security.password import hash_password, verify_and_update_password
from backend.libs.security.token import read_paseto_token_public_v4
from backend.services.user.crud import UserCRUD
from backend.services.user.exceptions import (
    InvalidResetPasswordTokenError,
    UserNotConfirmedError,
    UserNotFoundError,
)
from backend.services.user.models import User
from backend.services.user.operations.password import reset_password
from backend.services.user.operations.user import get_confirmed_user
from backend.services.user.schemas import ResetPasswordData, UserFilters
from backend.services.user.tasks import send_reset_password_email_task
from backend.services.user.types.password import (
    InvalidResetPasswordToken,
    RecoverPasswordResponse,
    ResetPasswordFailure,
    ResetPasswordInput,
    ResetPasswordResponse,
    ResetPasswordSuccess,
)

logger = logging.getLogger(__name__)

user_settings = get_settings().user


async def recover_password_resolver(info: Info, email: str) -> RecoverPasswordResponse:
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
    return RecoverPasswordResponse()


async def reset_password_resolver(
    info: Info,
    reset_password_input: Annotated[ResetPasswordInput, argument(name="input")],
) -> ResetPasswordResponse:
    try:
        reset_password_data = ResetPasswordData(
            token=reset_password_input.token,
            password=reset_password_input.password,
            password_hasher=hash_password,
        )
    except ValidationError as exc:
        return ResetPasswordFailure(problems=from_pydantic_error(exc))
    crud = UserCRUD(model=User, session=info.context.session)
    try:
        await reset_password(
            reset_password_data,
            partial(read_paseto_token_public_v4, key=user_settings.auth_public_key),
            verify_and_update_password,
            crud,
        )
    except (InvalidResetPasswordTokenError, UserNotConfirmedError):
        return ResetPasswordFailure(problems=[InvalidResetPasswordToken()])
    return ResetPasswordSuccess()
