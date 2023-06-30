from typing import Annotated

from pydantic import ValidationError
from strawberry import argument

from backend.libs.api.context import Info
from backend.libs.api.types import from_pydantic_error
from backend.libs.db.crud import CRUD
from backend.libs.security.password import hash_password, verify_and_update_password
from backend.services.user.controllers import authenticate, create_user
from backend.services.user.exceptions import (
    InvalidCredentialsError,
    UserAlreadyExistsError,
    UserNotConfirmedError,
)
from backend.services.user.models import User
from backend.services.user.schemas import (
    Credentials,
    UserCreateData,
    UserFilters,
    UserUpdateData,
)
from backend.services.user.tasks import send_confirmation_email_task
from backend.services.user.types import (
    CreateUserFailure,
    CreateUserResponse,
    CreateUserSuccess,
    InvalidCredentials,
    LoginFailure,
    LoginInput,
    LoginResponse,
    LoginSuccess,
    UserAlreadyExists,
    UserCreateInput,
    UserNotConfirmed,
)

UserCRUD = CRUD[User, UserCreateData, UserUpdateData, UserFilters]


async def create_user_resolver(
    info: Info, user_input: Annotated[UserCreateInput, argument(name="input")]
) -> CreateUserResponse:
    crud = UserCRUD(model=User, session=info.context.session)
    try:
        user_data = UserCreateData(
            email=user_input.email,
            password=user_input.password,
            password_hasher=hash_password,
        )
    except ValidationError as exc:
        return CreateUserFailure(problems=from_pydantic_error(exc))
    try:
        created_user = await create_user(user_data, crud)
    except UserAlreadyExistsError:
        return CreateUserFailure(problems=[UserAlreadyExists(email=user_input.email)])
    send_confirmation_email_task.delay(
        receiver=created_user.email, token="TODO: Generate token"  # nosec
    )
    return CreateUserSuccess(id=created_user.id, email=created_user.email)


async def login(
    info: Info, credentials_input: Annotated[LoginInput, argument(name="input")]
) -> LoginResponse:
    crud = UserCRUD(model=User, session=info.context.session)
    credentials = Credentials(
        email=credentials_input.username, password=credentials_input.password
    )
    try:
        await authenticate(credentials, verify_and_update_password, hash_password, crud)
    except InvalidCredentialsError:
        return LoginFailure(
            problems=[InvalidCredentials(username=credentials_input.username)]
        )
    except UserNotConfirmedError:
        return LoginFailure(
            problems=[UserNotConfirmed(username=credentials_input.username)]
        )
    return LoginSuccess(  # nosec
        access_token="TODO: Generate token",
        refresh_token="TODO: Generate token",
        token_type="TODO: Generate token",
    )
