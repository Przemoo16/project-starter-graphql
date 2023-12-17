from typing import Annotated

from pydantic import ValidationError
from strawberry import argument

from backend.libs.api.context import Info
from backend.libs.api.types import (
    convert_dataclass_to_dict,
    convert_pydantic_error_to_problems,
)
from backend.services.user.context import (
    async_password_hasher,
    async_password_validator,
    async_token_reader,
)
from backend.services.user.crud import UserCRUD
from backend.services.user.exceptions import (
    InvalidPasswordError,
    InvalidResetPasswordTokenError,
    InvalidResetPasswordTokenFingerprintError,
    UserNotFoundError,
)
from backend.services.user.models import User
from backend.services.user.operations.password import (
    PasswordManager,
    change_password,
    recover_password,
    reset_password,
)
from backend.services.user.schemas import PasswordChangeSchema, PasswordResetSchema
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


async def recover_password_resolver(info: Info, email: str) -> RecoverPasswordResponse:
    crud = UserCRUD(db=info.context.db)

    def send_reset_password_email(user: User) -> None:
        send_reset_password_email_task.delay(
            user_id=user.id, user_email=user.email, user_password=user.hashed_password
        )

    await recover_password(email, crud, send_reset_password_email)
    return RecoverPasswordResponse()


async def reset_password_resolver(
    info: Info,
    reset_password_input: Annotated[ResetPasswordInput, argument(name="input")],
) -> ResetPasswordResponse:
    try:
        schema = PasswordResetSchema.model_validate(
            convert_dataclass_to_dict(reset_password_input)
        )
    except ValidationError as exc:
        return ResetPasswordFailure(problems=convert_pydantic_error_to_problems(exc))

    password_manager = PasswordManager(
        validator=async_password_validator,
        hasher=async_password_hasher,
    )
    crud = UserCRUD(db=info.context.db)

    try:
        await reset_password(schema, async_token_reader, password_manager, crud)
    except (
        InvalidResetPasswordTokenError,
        UserNotFoundError,
        InvalidResetPasswordTokenFingerprintError,
    ):
        return ResetPasswordFailure(problems=[InvalidResetPasswordTokenProblem()])
    return ResetPasswordSuccess()


async def change_my_password_resolver(
    info: Info,
    change_password_input: Annotated[ChangeMyPasswordInput, argument(name="input")],
) -> ChangeMyPasswordResponse:
    user = await info.context.user
    try:
        schema = PasswordChangeSchema.model_validate(
            convert_dataclass_to_dict(change_password_input)
        )
    except ValidationError as exc:
        return ChangeMyPasswordFailure(problems=convert_pydantic_error_to_problems(exc))

    password_manager = PasswordManager(
        validator=async_password_validator,
        hasher=async_password_hasher,
    )
    crud = UserCRUD(db=info.context.db)

    try:
        await change_password(user, schema, password_manager, crud)
    except InvalidPasswordError:
        return ChangeMyPasswordFailure(problems=[InvalidPasswordProblem()])
    return ChangeMyPasswordSuccess()
