import strawberry
from pydantic import BaseModel, Field, ValidationError

from backend.libs.api.types import convert_to_dict, from_pydantic_error


def test_from_pydantic_error() -> None:
    class Model(BaseModel):
        full_name: str = Field(min_length=5)

    try:
        Model(full_name="Test")
    except ValidationError as exc:
        errors = from_pydantic_error(exc)

        assert len(errors) == 1
        assert errors[0].message
        assert errors[0].path == ["fullName"]

    else:
        raise AssertionError()


def test_convert_to_dict() -> None:
    @strawberry.type
    class Test:
        field_1: str = strawberry.UNSET
        field_2: str = strawberry.UNSET
        field_3: str = "test"

    test = Test(field_1="test")

    converted = convert_to_dict(test)

    assert converted == {
        "field_1": "test",
        "field_3": "test",
    }
