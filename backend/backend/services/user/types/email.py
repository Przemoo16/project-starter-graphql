from collections.abc import Sequence
from typing import Annotated
from uuid import UUID

import strawberry

from backend.libs.api.types import Problem


@strawberry.type
class ConfirmEmailSuccess:
    id: UUID
    email: str


@strawberry.type
class InvalidEmailConfirmationToken(Problem):
    message: str = "Provided token is invalid"


@strawberry.type
class UserAlreadyConfirmed(Problem):
    message: str = "The user has already been confirmed"


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
