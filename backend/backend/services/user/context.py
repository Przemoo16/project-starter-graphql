from functools import partial

from backend.config.settings import get_settings
from backend.libs.security.password import hash_password, verify_and_update_password
from backend.libs.security.token import (
    create_paseto_token_public_v4,
    read_paseto_token_public_v4,
)

user_settings = get_settings().user

TOKEN_READER = token_reader = partial(
    read_paseto_token_public_v4, key=user_settings.auth_public_key
)
TOKEN_CREATOR = partial(
    create_paseto_token_public_v4, key=user_settings.auth_private_key
)
PASSWORD_VALIDATOR = verify_and_update_password
PASSWORD_HASHER = hash_password
