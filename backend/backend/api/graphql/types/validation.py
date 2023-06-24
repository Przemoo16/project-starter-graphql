from collections.abc import Sequence

import strawberry
from pydantic import ValidationError

from backend.api.graphql.types.error import Problem


@strawberry.type
class InvalidInput(Problem):
    message: str
    path: Sequence[str]


def from_pydantic_error(exc: ValidationError) -> list[InvalidInput]:
    return [
        InvalidInput(message=error["msg"], path=[str(loc) for loc in error["loc"]])
        for error in exc.errors()
    ]
