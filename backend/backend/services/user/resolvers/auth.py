from functools import partial
from typing import Annotated

from strawberry import argument

from backend.config.settings import get_settings
from backend.libs.api.context import Info
from backend.services.user.context import (
    ASYNC_PASSWORD_HASHER,
    ASYNC_PASSWORD_VALIDATOR,
    ASYNC_TOKEN_CREATOR,
    ASYNC_TOKEN_READER,
)
from backend.services.user.crud import UserCRUD
from backend.services.user.exceptions import (
    InvalidPasswordError,
    InvalidRefreshTokenError,
    UserEmailNotConfirmedError,
    UserNotFoundError,
)
from backend.services.user.operations.auth import (
    AuthTokensManager,
    PasswordManager,
    login,
    refresh_token,
)
from backend.services.user.schemas import CredentialsSchema
from backend.services.user.types.auth import (
    InvalidCredentialsProblem,
    LoginFailure,
    LoginInput,
    LoginResponse,
    LoginSuccess,
    RefreshTokenResponse,
    UserEmailNotConfirmedProblem,
)

_user_settings = get_settings().user

ACCESS_TOKEN_CREATOR = partial(
    ASYNC_TOKEN_CREATOR,
    expiration=int(_user_settings.access_token_lifetime.total_seconds()),
)
REFRESH_TOKEN_CREATOR = partial(
    ASYNC_TOKEN_CREATOR,
    expiration=int(_user_settings.refresh_token_lifetime.total_seconds()),
)


async def login_resolver(
    info: Info, login_input: Annotated[LoginInput, argument(name="input")]
) -> LoginResponse:
    schema = CredentialsSchema(
        email=login_input.username, password=login_input.password
    )
    password_manager = PasswordManager(
        validator=ASYNC_PASSWORD_VALIDATOR,
        hasher=ASYNC_PASSWORD_HASHER,
    )
    tokens_manager = AuthTokensManager(
        access_token_creator=ACCESS_TOKEN_CREATOR,
        refresh_token_creator=REFRESH_TOKEN_CREATOR,
    )
    crud = UserCRUD(db=info.context.db)

    try:
        access_token, refresh_token_ = await login(
            schema, password_manager, tokens_manager, crud
        )
    except (UserNotFoundError, InvalidPasswordError):
        return LoginFailure(problems=[InvalidCredentialsProblem()])
    except UserEmailNotConfirmedError:
        return LoginFailure(problems=[UserEmailNotConfirmedProblem()])
    return LoginSuccess(
        access_token=access_token,
        refresh_token=refresh_token_,
        token_type="Bearer",  # nosec
    )


class RefreshTokenError(Exception):
    pass


async def refresh_token_resolver(token: str) -> RefreshTokenResponse:
    try:
        access_token = await refresh_token(
            token, ASYNC_TOKEN_READER, ACCESS_TOKEN_CREATOR
        )
    except InvalidRefreshTokenError as exc:
        msg = "Invalid token"
        raise RefreshTokenError(msg) from exc
    return RefreshTokenResponse(
        access_token=access_token,
        token_type="Bearer",  # nosec
    )
