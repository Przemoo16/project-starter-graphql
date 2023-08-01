from functools import partial
from typing import Annotated

from strawberry import argument

from backend.config.settings import get_settings
from backend.libs.api.context import Info
from backend.services.user.context import (
    PASSWORD_HASHER,
    PASSWORD_VALIDATOR,
    TOKEN_CREATOR,
    TOKEN_READER,
)
from backend.services.user.crud import UserCRUD
from backend.services.user.exceptions import (
    InvalidPasswordError,
    InvalidRefreshTokenError,
    UserNotConfirmedError,
    UserNotFoundError,
)
from backend.services.user.models import User
from backend.services.user.operations.auth import (
    AuthData,
    TokensCreationData,
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
    UserNotConfirmedProblem,
)

user_settings = get_settings().user

ACCESS_TOKEN_CREATOR = partial(
    TOKEN_CREATOR, expiration=int(user_settings.access_token_lifetime.total_seconds())
)
REFRESH_TOKEN_CREATOR = partial(
    TOKEN_CREATOR, expiration=int(user_settings.refresh_token_lifetime.total_seconds())
)


async def login_resolver(
    info: Info, login_input: Annotated[LoginInput, argument(name="input")]
) -> LoginResponse:
    credentials = CredentialsSchema(
        email=login_input.username, password=login_input.password
    )
    auth_data = AuthData(
        credentials=credentials,
        password_validator=PASSWORD_VALIDATOR,
        password_hasher=PASSWORD_HASHER,
    )
    tokens_data = TokensCreationData(
        access_token_creator=ACCESS_TOKEN_CREATOR,
        refresh_token_creator=REFRESH_TOKEN_CREATOR,
    )
    crud = UserCRUD(model=User, session=info.context.session)

    try:
        access_token, refresh_token_ = await login(auth_data, tokens_data, crud)
    except (UserNotFoundError, InvalidPasswordError):
        return LoginFailure(problems=[InvalidCredentialsProblem()])
    except UserNotConfirmedError:
        return LoginFailure(problems=[UserNotConfirmedProblem()])
    return LoginSuccess(
        access_token=access_token,
        refresh_token=refresh_token_,
        token_type="Bearer",  # nosec
    )


class RefreshTokenError(Exception):
    pass


async def refresh_token_resolver(info: Info, token: str) -> RefreshTokenResponse:
    crud = UserCRUD(model=User, session=info.context.session)

    try:
        access_token = await refresh_token(
            token, TOKEN_READER, ACCESS_TOKEN_CREATOR, crud
        )
    except (InvalidRefreshTokenError, UserNotFoundError, UserNotConfirmedError) as exc:
        msg = "Invalid token"
        raise RefreshTokenError(msg) from exc
    return RefreshTokenResponse(
        access_token=access_token,
        token_type="Bearer",  # nosec
    )
