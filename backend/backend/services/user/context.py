from functools import partial

from fastapi.concurrency import run_in_threadpool

from backend.config.settings import get_settings
from backend.libs.security.password import (
    async_hash_password,
    async_verify_and_update_password,
    hash_password,
    verify_and_update_password,
)
from backend.libs.security.token import (
    async_create_paseto_token_public_v4,
    async_read_paseto_token_public_v4,
    create_paseto_token_public_v4,
    read_paseto_token_public_v4,
)

_user_settings = get_settings().user


TOKEN_CREATOR = partial(
    create_paseto_token_public_v4, key=_user_settings.auth_private_key
)
ASYNC_TOKEN_CREATOR = partial(
    async_create_paseto_token_public_v4,
    key=_user_settings.auth_private_key,
    executor=run_in_threadpool,
)
TOKEN_READER = partial(read_paseto_token_public_v4, key=_user_settings.auth_public_key)
ASYNC_TOKEN_READER = partial(
    async_read_paseto_token_public_v4,
    key=_user_settings.auth_public_key,
    executor=run_in_threadpool,
)

PASSWORD_VALIDATOR = verify_and_update_password
ASYNC_PASSWORD_VALIDATOR = partial(
    async_verify_and_update_password, executor=run_in_threadpool
)
PASSWORD_HASHER = hash_password
ASYNC_PASSWORD_HASHER = partial(async_hash_password, executor=run_in_threadpool)
