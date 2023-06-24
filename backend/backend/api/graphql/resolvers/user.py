from backend.api.graphql.context import Info
from backend.api.graphql.types.user import (
    CreateUserResponse,
    User,
    UserAlreadyExists,
    UserCreateInput,
)
from backend.libs.db.crud import CRUD
from backend.services.user.controllers import create_user
from backend.services.user.exceptions import UserAlreadyExistsError
from backend.services.user.models import User as UserModel
from backend.services.user.schemas import UserCreateData, UserFilters, UserUpdateData

UserCRUD = CRUD[UserModel, UserCreateData, UserUpdateData, UserFilters]


async def create_user_resolver(info: Info, user: UserCreateInput) -> CreateUserResponse:
    crud = UserCRUD(model=UserModel, session=info.context.session)
    validated_data = validate_create_data(user)
    try:
        created_user = await create_user(validated_data, crud)
    except UserAlreadyExistsError:
        return UserAlreadyExists(email=user.email)
    return User(id=created_user.id, email=created_user.email)


def validate_create_data(user: UserCreateInput) -> UserCreateData:
    return UserCreateData(email=user.email, password=user.password)
