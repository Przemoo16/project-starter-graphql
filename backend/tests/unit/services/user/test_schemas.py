import pytest
from pydantic import ValidationError

from backend.services.user.schemas import UserCreateData, UserUpdateData


@pytest.mark.parametrize("schema", [UserCreateData, UserUpdateData])
def test_user_schema_invalid_email(
    schema: type[UserCreateData] | type[UserUpdateData],
) -> None:
    email = "invalid_email"
    password = "plain_password"

    with pytest.raises(ValidationError, match="email"):
        schema(
            email=email,
            password=password,
            password_hasher=lambda _: "hashed_password",
        )


@pytest.mark.parametrize("schema", [UserCreateData, UserUpdateData])
def test_user_schema_password_too_short(
    schema: type[UserCreateData] | type[UserUpdateData],
) -> None:
    email = "test@email.com"
    password = "p"

    with pytest.raises(ValidationError, match="password"):
        schema(
            email=email,
            password=password,
            password_hasher=lambda _: "hashed_password",
        )


@pytest.mark.parametrize("schema", [UserCreateData, UserUpdateData])
def test_user_schema_does_not_export_password_related_fields(
    schema: type[UserCreateData] | type[UserUpdateData],
) -> None:
    email = "test@email.com"
    password = "plain_password"

    data = schema(
        email=email,
        password=password,
        password_hasher=lambda _: "hashed_password",
    )

    data_dict = data.model_dump()
    assert "password_hasher" not in data_dict
    assert "password" not in data_dict


@pytest.mark.parametrize("schema", [UserCreateData, UserUpdateData])
def test_user_schema_hashes_password(
    schema: type[UserCreateData] | type[UserUpdateData],
) -> None:
    email = "test@email.com"
    password = "plain_password"

    data = schema(
        email=email,
        password=password,
        password_hasher=lambda _: "hashed_password",
    )

    assert data.hashed_password == "hashed_password"


def test_user_update_schema_no_password_provided() -> None:
    email = "test@email.com"

    data = UserUpdateData(email=email)

    assert not data.hashed_password


def test_user_update_schema_missing_password_hasher() -> None:
    password = "plain_password"

    with pytest.raises(ValidationError, match="Missing password hasher"):
        UserUpdateData(password=password)


def test_user_update_schema_hashed_password_provided() -> None:
    hashed_password = "hashed_password"

    data = UserUpdateData(hashed_password=hashed_password)

    assert data.hashed_password == "hashed_password"


def test_user_update_schema_both_password_and_hash_password_present() -> None:
    password = "plain_password"
    hashed_password = "hashed_password"

    with pytest.raises(
        ValidationError,
        match="Either 'password' or 'hashed_password' can be specified, not both.",
    ):
        UserUpdateData(
            password=password,
            hashed_password=hashed_password,
            password_hasher=lambda _: "hashed_password",
        )
