from pydantic import ValidationError

from backend.libs.api.context import Info
from backend.libs.api.types import from_pydantic_error
from backend.libs.db.crud import CRUD
from backend.libs.security.password import hash_password
from backend.services.user.controllers import create_user
from backend.services.user.exceptions import UserAlreadyExistsError
from backend.services.user.models import User
from backend.services.user.schemas import UserCreateData, UserFilters, UserUpdateData
from backend.services.user.tasks import send_confirmation_email_task
from backend.services.user.types import (
    CreateUserFailure,
    CreateUserResponse,
    CreateUserSuccess,
    UserAlreadyExists,
    UserCreateInput,
)

UserCRUD = CRUD[User, UserCreateData, UserUpdateData, UserFilters]


async def create_user_resolver(info: Info, user: UserCreateInput) -> CreateUserResponse:
    crud = UserCRUD(model=User, session=info.context.session)
    try:
        validated_data = _validate_create_data(user)
    except ValidationError as exc:
        return CreateUserFailure(problems=from_pydantic_error(exc))
    try:
        created_user = await create_user(validated_data, crud)
    except UserAlreadyExistsError:
        return CreateUserFailure(problems=[UserAlreadyExists(email=user.email)])
    send_confirmation_email_task.delay(
        receiver=created_user.email, token="TODO: Generate token"  # nosec
    )
    return CreateUserSuccess(id=created_user.id, email=created_user.email)


def _validate_create_data(user: UserCreateInput) -> UserCreateData:
    return UserCreateData(
        email=user.email, password=user.password, password_hasher=hash_password
    )
