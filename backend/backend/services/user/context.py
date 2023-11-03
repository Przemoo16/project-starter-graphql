from functools import partial

from fastapi.concurrency import run_in_threadpool

from backend.config.settings import settings
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
from backend.services.user.jinja import load_template

_user_settings = settings.user


token_creator = partial(
    create_paseto_token_public_v4, key=_user_settings.auth_private_key
)
async_token_creator = partial(
    async_create_paseto_token_public_v4,
    key=_user_settings.auth_private_key,
    executor=run_in_threadpool,
)
token_reader = partial(read_paseto_token_public_v4, key=_user_settings.auth_public_key)
async_token_reader = partial(
    async_read_paseto_token_public_v4,
    key=_user_settings.auth_public_key,
    executor=run_in_threadpool,
)

password_validator = verify_and_update_password
async_password_validator = partial(
    async_verify_and_update_password, executor=run_in_threadpool
)
password_hasher = hash_password
async_password_hasher = partial(async_hash_password, executor=run_in_threadpool)
template_loader = load_template
