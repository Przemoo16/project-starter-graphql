from typing import Annotated

from pydantic import ValidationError
from strawberry import argument

from backend.libs.api.context import Info
from backend.libs.api.types import (
    convert_dataclass_to_dict,
    convert_pydantic_error_to_problems,
)
from backend.services.user.context import async_password_hasher
from backend.services.user.crud import UserCRUD
from backend.services.user.exceptions import UserAlreadyExistsError
from backend.services.user.models import User as UserModel
from backend.services.user.operations.user import create_user, delete_user, update_user
from backend.services.user.schemas import UserCreateSchema, UserUpdateSchema
from backend.services.user.tasks import send_confirmation_email_task
from backend.services.user.types.user import (
    CreateUserFailure,
    CreateUserResponse,
    DeleteMeResponse,
    UpdateMeFailure,
    UpdateMeInput,
    UpdateMeResponse,
    User,
    UserAlreadyExistsProblem,
    UserCreateInput,
    get_user_type_from_model,
)


async def create_user_resolver(
    info: Info, user_input: Annotated[UserCreateInput, argument(name="input")]
) -> CreateUserResponse:
    try:
        schema = UserCreateSchema.model_validate(convert_dataclass_to_dict(user_input))
    except ValidationError as exc:
        return CreateUserFailure(problems=convert_pydantic_error_to_problems(exc))

    crud = UserCRUD(db=info.context.db)

    def send_confirmation_email(user: UserModel) -> None:
        send_confirmation_email_task.delay(user_id=user.id, user_email=user.email)

    try:
        created_user = await create_user(
            schema, async_password_hasher, crud, send_confirmation_email
        )
    except UserAlreadyExistsError:
        return CreateUserFailure(problems=[UserAlreadyExistsProblem()])
    return get_user_type_from_model(created_user)


async def get_me_resolver(info: Info) -> User:
    user = await info.context.user
    return get_user_type_from_model(user)


async def update_me_resolver(
    info: Info, user_input: Annotated[UpdateMeInput, argument(name="input")]
) -> UpdateMeResponse:
    user = await info.context.user

    try:
        schema = UserUpdateSchema.model_validate(convert_dataclass_to_dict(user_input))
    except ValidationError as exc:
        return UpdateMeFailure(problems=convert_pydantic_error_to_problems(exc))

    crud = UserCRUD(db=info.context.db)

    await update_user(user, schema, crud)
    return get_user_type_from_model(user)


async def delete_me_resolver(info: Info) -> DeleteMeResponse:
    user = await info.context.user
    crud = UserCRUD(db=info.context.db)

    await delete_user(user, crud)
    return DeleteMeResponse()
