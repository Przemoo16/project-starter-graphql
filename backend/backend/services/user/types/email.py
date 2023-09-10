from collections.abc import Sequence
from typing import Annotated

import strawberry

from backend.libs.api.types import Problem


@strawberry.type
class ConfirmEmailSuccess:
    message: str = " The user has been confirmed"


@strawberry.type
class InvalidEmailConfirmationTokenProblem(Problem):
    message: str = "Provided token is invalid"


@strawberry.type
class UserAlreadyConfirmedProblem(Problem):
    message: str = "The user has already been confirmed"


ConfirmEmailProblem = Annotated[
    InvalidEmailConfirmationTokenProblem | UserAlreadyConfirmedProblem,
    strawberry.union("ConfirmEmailProblem"),
]


@strawberry.type
class ConfirmEmailFailure:
    problems: Sequence[ConfirmEmailProblem]


ConfirmEmailResponse = Annotated[
    ConfirmEmailSuccess | ConfirmEmailFailure, strawberry.union("ConfirmEmailResponse")
]
