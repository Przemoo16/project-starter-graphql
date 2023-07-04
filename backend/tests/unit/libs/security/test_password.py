from backend.libs.security.password import hash_password, verify_and_update_password


def test_hash_and_verify_password() -> None:
    plain_password = "plain_password"

    hashed_password = hash_password(plain_password)
    verfied_password, _ = verify_and_update_password(plain_password, hashed_password)

    assert verfied_password
