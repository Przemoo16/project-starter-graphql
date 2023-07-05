from collections.abc import Mapping
from typing import Any

import orjson
from pyseto import DecryptError, Key, Paseto, VerifyError


class InvalidTokenError(Exception):
    pass


def create_paseto_token_public_v4(
    payload: Mapping[str, Any],
    expiration: int,
    key: str,
) -> str:
    paseto = Paseto.new(exp=expiration, include_iat=True)
    paseto_key = Key.new(version=4, purpose="public", key=key)
    token = paseto.encode(key=paseto_key, payload=dict(payload), serializer=orjson)
    return token.decode("utf-8")  # type: ignore[no-any-return]


def read_paseto_token_public_v4(token: str, key: str) -> dict[str, Any]:
    paseto = Paseto.new()
    paseto_key = Key.new(version=4, purpose="public", key=key)
    try:
        decoded_token = paseto.decode(
            keys=paseto_key,
            token=token,
            deserializer=orjson,
        )
    except (DecryptError, VerifyError, ValueError) as exc:
        raise InvalidTokenError() from exc
    return decoded_token.payload  # type: ignore[no-any-return]
