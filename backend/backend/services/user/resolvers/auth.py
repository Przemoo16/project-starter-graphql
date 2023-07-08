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
from backend.services.user.operations.auth import (
    create_access_token,
    create_refresh_token,
    login,
)
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
        user = await login(credentials, verify_and_update_password, hash_password, crud)
    except InvalidCredentialsError:
        return LoginFailure(problems=[InvalidCredentials()])
    except UserNotConfirmedError:
        return LoginFailure(problems=[UserNotConfirmed()])
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
