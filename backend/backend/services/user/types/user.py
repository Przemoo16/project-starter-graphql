from collections.abc import Sequence
from typing import Annotated, Self
from uuid import UUID

import strawberry

from backend.libs.api.types import InvalidInputProblem, Problem
from backend.services.user.models import User as UserModel


@strawberry.type
class User:
    id: UUID
    email: str
    full_name: str

    @classmethod
    def from_model(cls, model: UserModel) -> Self:
        return cls(id=model.id, email=model.email, full_name=model.full_name)


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
    full_name: str = strawberry.UNSET


@strawberry.type
class UpdateMeFailure:
    problems: Sequence[InvalidInputProblem]


UpdateMeResponse = Annotated[
    User | UpdateMeFailure, strawberry.union("UpdateMeResponse")
]


@strawberry.type
class DeleteMeResponse:
    message: str = "User has been deleted"
