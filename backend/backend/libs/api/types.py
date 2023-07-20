from dataclasses import asdict
from typing import Any, ClassVar, Protocol
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


class Dataclass(Protocol):
    __dataclass_fields__: ClassVar[dict[str, Any]]


def convert_to_dict(data: Dataclass) -> dict[Any, Any]:
    return {
        key: value
        for key, value in asdict(data).items()
        if value is not strawberry.UNSET
    }
