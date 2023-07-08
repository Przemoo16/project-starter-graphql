from collections.abc import Sequence
from typing import Annotated

import strawberry

from backend.libs.api.types import InvalidInput, Problem


@strawberry.type
class ResetPasswordResponse:
    message: str = "If provided valid email, the email to reset password has been sent"


@strawberry.input
class SetPasswordInput:
    token: str
    password: str


@strawberry.type
class SetPasswordSuccess:
    message: str = "New password has been set"


@strawberry.type
class InvalidResetPasswordToken(Problem):
    message: str = "Provided token is invalid"


SetPasswordProblem = Annotated[
    InvalidInput | InvalidResetPasswordToken, strawberry.union("SetPasswordProblem")
]


@strawberry.type
class SetPasswordFailure:
    problems: Sequence[SetPasswordProblem]


SetPasswordResponse = Annotated[
    SetPasswordSuccess | SetPasswordFailure, strawberry.union("SetPasswordResponse")
]
