import strawberry
from pydantic import ValidationError


@strawberry.interface
class Problem:
    message: str


@strawberry.type
class InvalidInput(Problem):
    message: str
    path: list[str]


def from_pydantic_error(exc: ValidationError) -> list[InvalidInput]:
    return [
        InvalidInput(message=error["msg"], path=[str(loc) for loc in error["loc"]])
        for error in exc.errors()
    ]
