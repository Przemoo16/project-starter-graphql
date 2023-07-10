from functools import partial

from backend.config.settings import get_settings
from backend.libs.api.context import Info
from backend.libs.security.token import read_paseto_token_public_v4
from backend.services.user.crud import UserCRUD
from backend.services.user.exceptions import (
    InvalidEmailConfirmationTokenError,
    UserAlreadyConfirmedError,
    UserNotFoundError,
)
from backend.services.user.models import User
from backend.services.user.operations.email import confirm_email
from backend.services.user.types.email import (
    ConfirmEmailFailure,
    ConfirmEmailResponse,
    ConfirmEmailSuccess,
    InvalidEmailConfirmationToken,
    UserAlreadyConfirmed,
)

user_settings = get_settings().user


async def confirm_email_resolver(info: Info, token: str) -> ConfirmEmailResponse:
    crud = UserCRUD(model=User, session=info.context.session)
    try:
        user = await confirm_email(
            token,
            partial(read_paseto_token_public_v4, key=user_settings.auth_public_key),
            crud,
        )
    except (InvalidEmailConfirmationTokenError, UserNotFoundError):
        return ConfirmEmailFailure(problems=[InvalidEmailConfirmationToken()])
    except UserAlreadyConfirmedError:
        return ConfirmEmailFailure(problems=[UserAlreadyConfirmed()])
    return ConfirmEmailSuccess(id=user.id, email=user.email)
