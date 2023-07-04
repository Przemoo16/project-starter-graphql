from collections.abc import Mapping
from typing import Any

import orjson
from pyseto import Key, Paseto


def create_paseto_token_public_v4(
    key: str,
    expiration: int,
    payload: Mapping[str, Any] | None = None,
    footer: Mapping[str, Any] | None = None,
) -> str:
    paseto = Paseto.new(exp=expiration, include_iat=True)
    paseto_key = Key.new(version=4, purpose="public", key=key)
    token = paseto.encode(
        key=paseto_key,
        payload=dict(payload) if payload else {},
        footer=dict(footer) if footer else {},
        serializer=orjson,
    )
    return token.decode("utf-8")  # type: ignore[no-any-return]
