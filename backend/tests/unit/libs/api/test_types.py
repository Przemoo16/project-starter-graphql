import strawberry
from pydantic import BaseModel, Field, ValidationError

from backend.libs.api.types import (
    convert_graphql_type_to_dict,
    convert_pydantic_error_to_problems,
)


def test_convert_pydantic_error_to_problems() -> None:
    class Model(BaseModel):
        test_field: str = Field(min_length=5)
        number: int = Field(gt=0)

    try:
        Model(test_field="Test", number=0)
    except ValidationError as exc:
        problems = convert_pydantic_error_to_problems(exc)

        assert len(problems) == 2
        assert problems[0].message
        assert problems[0].path == ["testField"]
        assert problems[1].message
        assert problems[1].path == ["number"]

    else:
        raise AssertionError()


def test_convert_graphql_type_to_dict() -> None:
    @strawberry.type
    class Test:
        field_1: str = strawberry.UNSET
        field_2: str = strawberry.UNSET
        field_3: str = "test"

    test = Test(field_1="test")

    converted = convert_graphql_type_to_dict(test)

    assert converted == {
        "field_1": "test",
        "field_3": "test",
    }
