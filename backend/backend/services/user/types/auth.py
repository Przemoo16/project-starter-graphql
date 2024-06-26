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
class InvalidCredentialsProblem(Problem):
    message: str = "Provided credentials are invalid"


@strawberry.type
class UserEmailNotConfirmedProblem(Problem):
    message: str = "The user email has not been confirmed"


LoginProblem = Annotated[
    InvalidCredentialsProblem | UserEmailNotConfirmedProblem,
    strawberry.union("LoginProblem"),
]


@strawberry.type
class LoginFailure:
    problems: Sequence[LoginProblem]


LoginResponse = Annotated[
    LoginSuccess | LoginFailure, strawberry.union("LoginResponse")
]


@strawberry.type
class RefreshTokenResponse:
    access_token: str
    token_type: str
