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
from backend.services.user.operations.password import set_password
from backend.services.user.operations.user import get_confirmed_user
from backend.services.user.schemas import SetPasswordData, UserFilters
from backend.services.user.tasks import send_reset_password_email_task
from backend.services.user.types.password import (
    InvalidResetPasswordToken,
    ResetPasswordResponse,
    SetPasswordFailure,
    SetPasswordInput,
    SetPasswordResponse,
    SetPasswordSuccess,
)

logger = logging.getLogger(__name__)

user_settings = get_settings().user


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
    return ResetPasswordResponse()


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
    except (InvalidResetPasswordTokenError, UserNotConfirmedError):
        return SetPasswordFailure(problems=[InvalidResetPasswordToken()])
    return SetPasswordSuccess()
