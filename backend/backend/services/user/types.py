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
    message: str = "User with provided email already exists"
    email: str


CreateUserProblem = Annotated[
    InvalidInput | UserAlreadyExists, strawberry.union("CreateUserProblem")
]


@strawberry.type
class CreateUserFailure:
    problems: Sequence[CreateUserProblem]


CreateUserResponse = Annotated[
    CreateUserSuccess | CreateUserFailure, strawberry.union("CreateUserResponse")
]


@strawberry.type
class ConfirmEmailSuccess:
    id: UUID
    email: str


@strawberry.type
class InvalidEmailConfirmationToken(Problem):
    message: str = "Provided token is invalid"
    token: str


@strawberry.type
class UserAlreadyConfirmed(Problem):
    message: str = "User has already been confirmed"
    email: str


ConfirmEmailProblem = Annotated[
    InvalidEmailConfirmationToken | UserAlreadyConfirmed,
    strawberry.union("ConfirmEmailProblem"),
]


@strawberry.type
class ConfirmEmailFailure:
    problems: Sequence[ConfirmEmailProblem]


ConfirmEmailResponse = Annotated[
    ConfirmEmailSuccess | ConfirmEmailFailure, strawberry.union("ConfirmEmailResponse")
]


@strawberry.input
class LoginInput:
    username: str
    password: str


@strawberry.type
class LoginSuccess:
    access_token: str
    refresh_token: str
    token_type: str


@strawberry.type
class InvalidCredentials(Problem):
    message: str = "Provided credentials are not valid"
    username: str


@strawberry.type
class UserNotConfirmed(Problem):
    message: str = "User has not confirmed the email"
    username: str


LoginProblem = Annotated[
    InvalidCredentials | UserNotConfirmed, strawberry.union("LoginProblem")
]


@strawberry.type
class LoginFailure:
    problems: Sequence[LoginProblem]


LoginResponse = Annotated[
    LoginSuccess | LoginFailure, strawberry.union("LoginResponse")
]
