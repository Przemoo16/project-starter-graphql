import strawberry
from pydantic import BaseModel, Field, ValidationError

from backend.libs.api.types import convert_to_dict, from_pydantic_error


def test_from_pydantic_error() -> None:
    class DummyModel(BaseModel):
        string: str = Field(min_length=5)

    try:
        DummyModel(string="test")
    except ValidationError as exc:
        errors = from_pydantic_error(exc)

        assert all(error.message and error.path for error in errors)

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
