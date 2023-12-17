from collections.abc import Sequence
from typing import Annotated
from uuid import UUID

import strawberry

from backend.libs.api.types import InvalidInputProblem, Problem
from backend.services.user.models import User as UserModel


@strawberry.type
class User:
    id: UUID
    email: str
    full_name: str


def get_user_type_from_model(model: UserModel) -> User:
    return User(id=model.id, email=model.email, full_name=model.full_name)


@strawberry.input
class UserCreateInput:
    email: str
    password: str
    full_name: str


@strawberry.type
class UserAlreadyExistsProblem(Problem):
    message: str = "User with provided data already exists"


CreateUserProblem = Annotated[
    InvalidInputProblem | UserAlreadyExistsProblem,
    strawberry.union("CreateUserProblem"),
]


@strawberry.type
class CreateUserFailure:
    problems: Sequence[CreateUserProblem]


CreateUserResponse = Annotated[
    User | CreateUserFailure, strawberry.union("CreateUserResponse")
]


@strawberry.input
class UpdateMeInput:
    full_name: str | None = strawberry.UNSET


@strawberry.type
class UpdateMeFailure:
    problems: Sequence[InvalidInputProblem]


UpdateMeResponse = Annotated[
    User | UpdateMeFailure, strawberry.union("UpdateMeResponse")
]


@strawberry.type
class DeleteMeResponse:
    message: str = "User has been deleted"
