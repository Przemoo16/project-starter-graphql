from pydantic import BaseModel, Field, ValidationError

from backend.libs.api.types import from_pydantic_error


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
