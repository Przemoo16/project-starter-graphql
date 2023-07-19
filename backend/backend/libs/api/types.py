from uuid import UUID

import strawberry
from pydantic import ValidationError


@strawberry.interface
class Problem:
    message: str


@strawberry.type
class InvalidInputProblem(Problem):
    message: str
    path: list[str]


def from_pydantic_error(exc: ValidationError) -> list[InvalidInputProblem]:
    return [
        InvalidInputProblem(
            message=error["msg"], path=[str(loc) for loc in error["loc"]]
        )
        for error in exc.errors()
    ]


@strawberry.type
class User:
    id: UUID
    email: str
