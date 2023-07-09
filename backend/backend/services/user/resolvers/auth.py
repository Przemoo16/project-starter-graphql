from functools import partial
from typing import Annotated

from strawberry import argument

from backend.config.settings import get_settings
from backend.libs.api.context import Info
from backend.libs.security.password import hash_password, verify_and_update_password
from backend.libs.security.token import create_paseto_token_public_v4
from backend.services.user.crud import UserCRUD
from backend.services.user.exceptions import (
    InvalidCredentialsError,
    UserNotConfirmedError,
)
from backend.services.user.models import User
from backend.services.user.operations.auth import authenticate, login
from backend.services.user.schemas import Credentials
from backend.services.user.types.auth import (
    InvalidCredentials,
    LoginFailure,
    LoginInput,
    LoginResponse,
    LoginSuccess,
    UserNotConfirmed,
)

user_settings = get_settings().user


async def login_resolver(
    info: Info, credentials_input: Annotated[LoginInput, argument(name="input")]
) -> LoginResponse:
    crud = UserCRUD(model=User, session=info.context.session)
    credentials = Credentials(
        email=credentials_input.username, password=credentials_input.password
    )
    try:
        user = await authenticate(
            credentials, verify_and_update_password, hash_password, crud
        )
    except InvalidCredentialsError:
        return LoginFailure(problems=[InvalidCredentials()])
    except UserNotConfirmedError:
        return LoginFailure(problems=[UserNotConfirmed()])
    access_token, refresh_token = await login(
        user=user,
        access_token_creator=partial(
            create_paseto_token_public_v4,
            expiration=int(user_settings.access_token_lifetime.total_seconds()),
            key=user_settings.auth_private_key.get_secret_value(),
        ),
        refresh_token_creator=partial(
            create_paseto_token_public_v4,
            expiration=int(user_settings.refresh_token_lifetime.total_seconds()),
            key=user_settings.auth_private_key.get_secret_value(),
        ),
        crud=crud,
    )
    return LoginSuccess(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="Bearer",  # nosec
    )
