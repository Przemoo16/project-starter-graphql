from collections.abc import Sequence
from typing import Annotated

import strawberry

from backend.libs.api.types import InvalidInputProblem, Problem, User


@strawberry.input
class UserCreateInput:
    email: str
    password: str


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
    email: str = strawberry.UNSET


UpdateMeProblem = Annotated[
    InvalidInputProblem | UserAlreadyExistsProblem,
    strawberry.union("UpdateMeProblem"),
]


@strawberry.type
class UpdateMeFailure:
    problems: Sequence[UpdateMeProblem]


UpdateMeResponse = Annotated[
    User | UpdateMeFailure, strawberry.union("UpdateMeResponse")
]


@strawberry.type
class DeleteMeResponse:
    message: str = "User has been deleted"
