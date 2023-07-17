from collections.abc import Sequence
from typing import Annotated
from uuid import UUID

import strawberry

from backend.libs.api.types import InvalidInputProblem, Problem


@strawberry.input
class UserCreateInput:
    email: str
    password: str


@strawberry.type
class CreateUserSuccess:
    id: UUID
    email: str


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
    CreateUserSuccess | CreateUserFailure, strawberry.union("CreateUserResponse")
]
