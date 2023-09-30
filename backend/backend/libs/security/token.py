from collections.abc import Mapping
from typing import Any

import orjson
from pyseto import DecryptError, Key, Paseto, VerifyError


class InvalidTokenError(Exception):
    pass


_paseto = Paseto.new(include_iat=True)


def create_paseto_token_public_v4(
    payload: Mapping[str, Any],
    expiration: int,
    key: bytes | str,
) -> str:
    paseto_key = Key.new(version=4, purpose="public", key=key)
    token = _paseto.encode(
        key=paseto_key, payload=dict(payload), serializer=orjson, exp=expiration
    )
    return token.decode("utf-8")  # type: ignore[no-any-return]


def read_paseto_token_public_v4(token: str, key: bytes | str) -> dict[str, Any]:
    paseto_key = Key.new(version=4, purpose="public", key=key)
    try:
        decoded_token = _paseto.decode(
            keys=paseto_key,
            token=token,
            deserializer=orjson,
        )
    except (DecryptError, VerifyError, ValueError) as exc:
        raise InvalidTokenError() from exc
    return decoded_token.payload  # type: ignore[no-any-return]
