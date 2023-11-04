from typing import Annotated

from pydantic import ValidationError
from strawberry import argument

from backend.libs.api.context import Info
from backend.libs.api.types import convert_to_dict, from_pydantic_error
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
)


async def create_user_resolver(
    info: Info, user_input: Annotated[UserCreateInput, argument(name="input")]
) -> CreateUserResponse:
    try:
        schema = UserCreateSchema.model_validate(convert_to_dict(user_input))
    except ValidationError as exc:
        return CreateUserFailure(problems=from_pydantic_error(exc))

    crud = UserCRUD(db=info.context.db)

    def send_confirmation_email(user: UserModel) -> None:
        send_confirmation_email_task.delay(user_id=user.id, user_email=user.email)

    try:
        created_user = await create_user(
            schema, async_password_hasher, crud, send_confirmation_email
        )
    except UserAlreadyExistsError:
        return CreateUserFailure(problems=[UserAlreadyExistsProblem()])
    return User.from_model(created_user)


async def get_me_resolver(info: Info) -> User:
    user = await info.context.user
    return User.from_model(user)


async def update_me_resolver(
    info: Info, user_input: Annotated[UpdateMeInput, argument(name="input")]
) -> UpdateMeResponse:
    user = await info.context.user

    try:
        schema = UserUpdateSchema.model_validate(convert_to_dict(user_input))
    except ValidationError as exc:
        return UpdateMeFailure(problems=from_pydantic_error(exc))

    crud = UserCRUD(db=info.context.db)

    updated_user = await update_user(user, schema, crud)
    return User.from_model(updated_user)


async def delete_me_resolver(info: Info) -> DeleteMeResponse:
    user = await info.context.user
    crud = UserCRUD(db=info.context.db)

    await delete_user(user, crud)
    return DeleteMeResponse()
