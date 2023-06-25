from collections.abc import Sequence
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
    message: str = "User with provided email already exists"
    email: str


@strawberry.type
class CreateUserFailure:
    problems: Sequence[InvalidInput | UserAlreadyExists]


CreateUserResponse = CreateUserSuccess | CreateUserFailure
