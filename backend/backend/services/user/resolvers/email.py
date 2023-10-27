from backend.libs.api.context import Info
from backend.services.user.context import ASYNC_TOKEN_READER
from backend.services.user.crud import UserCRUD
from backend.services.user.exceptions import (
    InvalidEmailConfirmationTokenError,
    UserEmailAlreadyConfirmedError,
    UserNotFoundError,
)
from backend.services.user.operations.email import confirm_email
from backend.services.user.types.email import (
    ConfirmEmailFailure,
    ConfirmEmailResponse,
    ConfirmEmailSuccess,
    InvalidEmailConfirmationTokenProblem,
    UserEmailAlreadyConfirmedProblem,
)


async def confirm_email_resolver(info: Info, token: str) -> ConfirmEmailResponse:
    crud = UserCRUD(db=info.context.db)

    try:
        await confirm_email(token, ASYNC_TOKEN_READER, crud)
    except (InvalidEmailConfirmationTokenError, UserNotFoundError):
        return ConfirmEmailFailure(problems=[InvalidEmailConfirmationTokenProblem()])
    except UserEmailAlreadyConfirmedError:
        return ConfirmEmailFailure(problems=[UserEmailAlreadyConfirmedProblem()])
    return ConfirmEmailSuccess()
