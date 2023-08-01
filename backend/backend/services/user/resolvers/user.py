from typing import Annotated

from pydantic import ValidationError
from strawberry import argument

from backend.libs.api.context import Info
from backend.libs.api.types import User, convert_to_dict, from_pydantic_error
from backend.services.user.context import PASSWORD_HASHER
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
    UserAlreadyExistsProblem,
    UserCreateInput,
)


def send_confirmation_email(user: UserModel) -> None:
    send_confirmation_email_task.delay(user_id=user.id, user_email=user.email)


async def create_user_resolver(
    info: Info, user_input: Annotated[UserCreateInput, argument(name="input")]
) -> CreateUserResponse:
    try:
        schema = UserCreateSchema.model_validate(convert_to_dict(user_input))
    except ValidationError as exc:
        return CreateUserFailure(problems=from_pydantic_error(exc))

    crud = UserCRUD(model=UserModel, session=info.context.session)

    try:
        created_user = await create_user(
            schema, PASSWORD_HASHER, crud, send_confirmation_email
        )
    except UserAlreadyExistsError:
        return CreateUserFailure(problems=[UserAlreadyExistsProblem()])
    return User(id=created_user.id, email=created_user.email)


async def get_me_resolver(info: Info) -> User:
    user = await info.context.user
    return User(id=user.id, email=user.email)


async def update_me_resolver(
    info: Info, user_input: Annotated[UpdateMeInput, argument(name="input")]
) -> UpdateMeResponse:
    user = await info.context.user

    try:
        schema = UserUpdateSchema.model_validate(convert_to_dict(user_input))
    except ValidationError as exc:
        return UpdateMeFailure(problems=from_pydantic_error(exc))

    crud = UserCRUD(model=UserModel, session=info.context.session)

    try:
        updated_user = await update_user(user, schema, crud, send_confirmation_email)
    except UserAlreadyExistsError:
        return UpdateMeFailure(problems=[UserAlreadyExistsProblem()])
    return User(id=updated_user.id, email=updated_user.email)


async def delete_me_resolver(info: Info) -> DeleteMeResponse:
    user = await info.context.user
    crud = UserCRUD(model=UserModel, session=info.context.session)

    await delete_user(user, crud)
    return DeleteMeResponse()
