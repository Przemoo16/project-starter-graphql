from passlib.context import CryptContext

from backend.libs.types.asynchronous import AsyncExecutor

_pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_and_update_password(
    plain_password: str, hashed_password: str
) -> tuple[bool, str | None]:
    return _pwd_context.verify_and_update(plain_password, hashed_password)


async def async_verify_and_update_password(
    plain_password: str,
    hashed_password: str,
    executor: AsyncExecutor,
) -> tuple[bool, str | None]:
    return await executor(verify_and_update_password, plain_password, hashed_password)


def hash_password(password: str) -> str:
    return _pwd_context.hash(password)


async def async_hash_password(password: str, executor: AsyncExecutor) -> str:
    return await executor(hash_password, password)
