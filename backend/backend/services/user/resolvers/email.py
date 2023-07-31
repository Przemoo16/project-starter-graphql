from backend.libs.api.context import Info
from backend.libs.api.types import User
from backend.services.user.context import TOKEN_READER
from backend.services.user.crud import UserCRUD
from backend.services.user.exceptions import (
    InvalidEmailConfirmationTokenError,
    UserAlreadyConfirmedError,
    UserNotFoundError,
)
from backend.services.user.models import User as UserModel
from backend.services.user.operations.email import confirm_email
from backend.services.user.types.email import (
    ConfirmEmailFailure,
    ConfirmEmailResponse,
    InvalidEmailConfirmationTokenProblem,
    UserAlreadyConfirmedProblem,
)


async def confirm_email_resolver(info: Info, token: str) -> ConfirmEmailResponse:
    crud = UserCRUD(model=UserModel, session=info.context.session)

    try:
        user = await confirm_email(token, TOKEN_READER, crud)
    except (InvalidEmailConfirmationTokenError, UserNotFoundError):
        return ConfirmEmailFailure(problems=[InvalidEmailConfirmationTokenProblem()])
    except UserAlreadyConfirmedError:
        return ConfirmEmailFailure(problems=[UserAlreadyConfirmedProblem()])
    return User(id=user.id, email=user.email)
