import pytest

from backend.services.user.schemas import UserCreateData, UserUpdateData


@pytest.mark.parametrize("data_class", [UserCreateData, UserUpdateData])
def test_user_data_does_not_export_hash_password_algorithm(
    data_class: type[UserCreateData] | type[UserUpdateData],
) -> None:
    email = "test@email.com"
    password = "plain_password"

    data = data_class(
        email=email,
        password=password,
        hash_password_algorithm=lambda _: "hashed_password",
    )

    assert "hash_password_algorithm" not in data.dict()


@pytest.mark.parametrize("data_class", [UserCreateData, UserUpdateData])
def test_user_data_hashes_password(
    data_class: type[UserCreateData] | type[UserUpdateData],
) -> None:
    email = "test@email.com"
    password = "plain_password"

    data = data_class(
        email=email,
        password=password,
        hash_password_algorithm=lambda _: "hashed_password",
    )

    assert data.hashed_password == "hashed_password"


def test_user_update_data_missing_password_hash_algorithm() -> None:
    password = "plain_password"

    with pytest.raises(ValueError, match="Missing hash password algorithm"):
        UserUpdateData(password=password)
