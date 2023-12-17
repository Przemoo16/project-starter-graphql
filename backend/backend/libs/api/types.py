from dataclasses import asdict
from typing import Any

import strawberry
from pydantic import ValidationError
from pydantic.alias_generators import to_camel

from backend.libs.types.dataclass import Dataclass


@strawberry.interface
class Problem:
    message: str


@strawberry.type
class InvalidInputProblem(Problem):
    message: str
    path: list[str]


def convert_pydantic_error_to_problems(
    exc: ValidationError,
) -> list[InvalidInputProblem]:
    return [
        InvalidInputProblem(
            message=error["msg"], path=[to_camel(str(loc)) for loc in error["loc"]]
        )
        for error in exc.errors()
    ]


def convert_dataclass_to_dict(data: Dataclass) -> dict[Any, Any]:
    return {
        key: value
        for key, value in asdict(data).items()
        if value is not strawberry.UNSET
    }
