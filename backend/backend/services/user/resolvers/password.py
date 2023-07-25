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
    InvalidPasswordError,
    InvalidResetPasswordTokenError,
    InvalidResetPasswordTokenFingerprintError,
    UserNotConfirmedError,
    UserNotFoundError,
)
from backend.services.user.models import User
from backend.services.user.operations.password import (
    change_password,
    recover_password,
    reset_password,
)
from backend.services.user.schemas import ChangePasswordData, ResetPasswordData
from backend.services.user.tasks import send_reset_password_email_task
from backend.services.user.types.password import (
    ChangeMyPasswordFailure,
    ChangeMyPasswordInput,
    ChangeMyPasswordResponse,
    ChangeMyPasswordSuccess,
    InvalidPasswordProblem,
    InvalidResetPasswordTokenProblem,
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

    def send_recovery_email(user: User) -> None:
        send_reset_password_email_task.delay(
            user_id=user.id, user_email=user.email, user_password=user.hashed_password
        )

    await recover_password(email, crud, send_recovery_email)
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

    token_reader = partial(
        read_paseto_token_public_v4, key=user_settings.auth_public_key
    )
    crud = UserCRUD(model=User, session=info.context.session)

    try:
        await reset_password(
            reset_password_data, token_reader, verify_and_update_password, crud
        )
    except (
        InvalidResetPasswordTokenError,
        UserNotFoundError,
        InvalidResetPasswordTokenFingerprintError,
        UserNotConfirmedError,
    ):
        return ResetPasswordFailure(problems=[InvalidResetPasswordTokenProblem()])
    return ResetPasswordSuccess()


async def change_my_password_resolver(
    info: Info,
    change_password_input: Annotated[ChangeMyPasswordInput, argument(name="input")],
) -> ChangeMyPasswordResponse:
    user = await info.context.user
    try:
        change_password_data = ChangePasswordData(
            current_password=change_password_input.current_password,
            new_password=change_password_input.new_password,
            password_hasher=hash_password,
        )
    except ValidationError as exc:
        return ChangeMyPasswordFailure(problems=from_pydantic_error(exc))

    crud = UserCRUD(model=User, session=info.context.session)

    try:
        await change_password(
            user, change_password_data, verify_and_update_password, crud
        )
    except InvalidPasswordError:
        return ChangeMyPasswordFailure(problems=[InvalidPasswordProblem()])
    return ChangeMyPasswordSuccess()
