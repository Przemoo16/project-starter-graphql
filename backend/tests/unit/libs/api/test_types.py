import strawberry
from pydantic import BaseModel, Field, ValidationError

from backend.libs.api.types import convert_to_dict, from_pydantic_error


def test_from_pydantic_error_converts_pydantic_errors_to_problem_types() -> None:
    class Model(BaseModel):
        test_field: str = Field(min_length=5)
        number: int = Field(gt=0)

    try:
        Model(test_field="Test", number=0)
    except ValidationError as exc:
        errors = from_pydantic_error(exc)

        assert len(errors) == 2
        assert errors[0].message
        assert errors[0].path == ["testField"]
        assert errors[1].message
        assert errors[1].path == ["number"]

    else:
        raise AssertionError()


def test_convert_to_dict_converts_dataclass_to_dictionary() -> None:
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
