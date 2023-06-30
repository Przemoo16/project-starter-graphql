from passlib.context import CryptContext

_pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_and_update_password(
    plain_password: str, hashed_password: str
) -> tuple[bool, str | None]:
    return _pwd_context.verify_and_update(plain_password, hashed_password)


def hash_password(password: str) -> str:
    return _pwd_context.hash(password)
