from collections.abc import Sequence
from typing import Annotated
from uuid import UUID

import strawberry

from backend.libs.api.types import InvalidInput, Problem


@strawberry.input
class UserCreateInput:
    email: str
    password: str


@strawberry.type
class CreateUserSuccess:
    id: UUID
    email: str


@strawberry.type
class UserAlreadyExists(Problem):
    message: str = "User with provided data already exists"


CreateUserProblem = Annotated[
    InvalidInput | UserAlreadyExists, strawberry.union("CreateUserProblem")
]


@strawberry.type
class CreateUserFailure:
    problems: Sequence[CreateUserProblem]


CreateUserResponse = Annotated[
    CreateUserSuccess | CreateUserFailure, strawberry.union("CreateUserResponse")
]
