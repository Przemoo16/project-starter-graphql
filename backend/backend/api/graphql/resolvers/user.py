from pydantic import ValidationError

from backend.api.graphql.context import Info
from backend.api.graphql.types.user import (
    CreateUserFailure,
    CreateUserResponse,
    CreateUserSuccess,
    UserAlreadyExists,
    UserCreateInput,
)
from backend.api.graphql.types.validation import from_pydantic_error
from backend.libs.db.crud import CRUD
from backend.services.user.controllers import create_user
from backend.services.user.exceptions import UserAlreadyExistsError
from backend.services.user.models import User
from backend.services.user.schemas import UserCreateData, UserFilters, UserUpdateData

UserCRUD = CRUD[User, UserCreateData, UserUpdateData, UserFilters]


async def create_user_resolver(info: Info, user: UserCreateInput) -> CreateUserResponse:
    crud = UserCRUD(model=User, session=info.context.session)
    try:
        validated_data = validate_create_data(user)
    except ValidationError as exc:
        return CreateUserFailure(problems=from_pydantic_error(exc))
    try:
        created_user = await create_user(validated_data, crud)
    except UserAlreadyExistsError:
        return CreateUserFailure(problems=[UserAlreadyExists(email=user.email)])
    return CreateUserSuccess(id=created_user.id, email=created_user.email)


def validate_create_data(user: UserCreateInput) -> UserCreateData:
    return UserCreateData(email=user.email, password=user.password)
