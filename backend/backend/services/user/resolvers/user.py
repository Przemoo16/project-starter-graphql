from typing import Annotated

from pydantic import ValidationError
from strawberry import argument

from backend.libs.api.context import Info
from backend.libs.api.types import from_pydantic_error
from backend.libs.security.password import hash_password
from backend.services.user.crud import UserCRUD
from backend.services.user.exceptions import UserAlreadyExistsError
from backend.services.user.models import User
from backend.services.user.operations.user import create_user
from backend.services.user.schemas import UserCreateData
from backend.services.user.tasks import send_confirmation_email_task
from backend.services.user.types.user import (
    CreateUserFailure,
    CreateUserResponse,
    CreateUserSuccess,
    UserAlreadyExists,
    UserCreateInput,
)


async def create_user_resolver(
    info: Info, user_input: Annotated[UserCreateInput, argument(name="input")]
) -> CreateUserResponse:
    try:
        user_data = UserCreateData(
            email=user_input.email,
            password=user_input.password,
            password_hasher=hash_password,
        )
    except ValidationError as exc:
        return CreateUserFailure(problems=from_pydantic_error(exc))

    def send_confirmation_email(user: User) -> None:
        send_confirmation_email_task.delay(user_id=user.id, user_email=user.email)

    crud = UserCRUD(model=User, session=info.context.session)
    try:
        created_user = await create_user(user_data, crud, send_confirmation_email)
    except UserAlreadyExistsError:
        return CreateUserFailure(problems=[UserAlreadyExists()])
    return CreateUserSuccess(id=created_user.id, email=created_user.email)
