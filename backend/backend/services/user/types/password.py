from collections.abc import Sequence
from typing import Annotated

import strawberry

from backend.libs.api.types import InvalidInputProblem, Problem


@strawberry.type
class RecoverPasswordResponse:
    message: str = "If provided valid email, the email to reset password has been sent"


@strawberry.input
class ResetPasswordInput:
    token: str
    password: str


@strawberry.type
class ResetPasswordSuccess:
    message: str = "New password has been set"


@strawberry.type
class InvalidResetPasswordTokenProblem(Problem):
    message: str = "Provided token is invalid"


ResetPasswordProblem = Annotated[
    InvalidInputProblem | InvalidResetPasswordTokenProblem,
    strawberry.union("ResetPasswordProblem"),
]


@strawberry.type
class ResetPasswordFailure:
    problems: Sequence[ResetPasswordProblem]


ResetPasswordResponse = Annotated[
    ResetPasswordSuccess | ResetPasswordFailure,
    strawberry.union("ResetPasswordResponse"),
]


@strawberry.input
class ChangeMyPasswordInput:
    current_password: str
    new_password: str


@strawberry.type
class ChangeMyPasswordSuccess:
    message: str = "Password has been changed"


@strawberry.type
class InvalidPasswordProblem(Problem):
    message: str = "Provided password is invalid"


ChangeMyPasswordProblem = Annotated[
    InvalidInputProblem | InvalidPasswordProblem,
    strawberry.union("ChangeMyPasswordProblem"),
]


@strawberry.type
class ChangeMyPasswordFailure:
    problems: Sequence[ChangeMyPasswordProblem]


ChangeMyPasswordResponse = Annotated[
    ChangeMyPasswordSuccess | ChangeMyPasswordFailure,
    strawberry.union("ChangeMyPasswordResponse"),
]
