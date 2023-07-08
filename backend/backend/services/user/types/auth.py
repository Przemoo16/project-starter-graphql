from collections.abc import Sequence
from typing import Annotated

import strawberry

from backend.libs.api.types import Problem


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
    message: str = "Provided credentials are invalid"


@strawberry.type
class UserNotConfirmed(Problem):
    message: str = "The user is not confirmed"


LoginProblem = Annotated[
    InvalidCredentials | UserNotConfirmed, strawberry.union("LoginProblem")
]


@strawberry.type
class LoginFailure:
    problems: Sequence[LoginProblem]


LoginResponse = Annotated[
    LoginSuccess | LoginFailure, strawberry.union("LoginResponse")
]
