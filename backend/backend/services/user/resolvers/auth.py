from functools import partial
from typing import Annotated

from strawberry import argument

from backend.config.settings import settings
from backend.libs.api.context import Info
from backend.services.user.context import (
    async_password_hasher,
    async_password_validator,
    async_token_creator,
    async_token_reader,
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

_user_settings = settings.user

_access_token_creator = partial(
    async_token_creator,
    expiration=int(_user_settings.access_token_lifetime.total_seconds()),
)
_refresh_token_creator = partial(
    async_token_creator,
    expiration=int(_user_settings.refresh_token_lifetime.total_seconds()),
)


class _RefreshTokenError(Exception):
    pass


async def login_resolver(
    info: Info, login_input: Annotated[LoginInput, argument(name="input")]
) -> LoginResponse:
    schema = CredentialsSchema(
        email=login_input.username, password=login_input.password
    )
    password_manager = PasswordManager(
        validator=async_password_validator,
        hasher=async_password_hasher,
    )
    tokens_manager = AuthTokensManager(
        access_token_creator=_access_token_creator,
        refresh_token_creator=_refresh_token_creator,
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
        token_type="Bearer",  # nosec B106
    )


async def refresh_token_resolver(token: str) -> RefreshTokenResponse:
    try:
        access_token = await refresh_token(
            token, async_token_reader, _access_token_creator
        )
    except InvalidRefreshTokenError as exc:
        msg = "Invalid token"
        raise _RefreshTokenError(msg) from exc
    return RefreshTokenResponse(
        access_token=access_token,
        token_type="Bearer",  # nosec B106
    )
