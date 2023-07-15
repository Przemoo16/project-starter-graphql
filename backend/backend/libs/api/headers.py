from collections.abc import Mapping
from typing import Any


class BearerTokenNotFoundError(Exception):
    pass


def read_bearer_token(headers: Mapping[Any, str]) -> str:
    auth_header = headers.get("Authentication")
    if not auth_header:
        raise BearerTokenNotFoundError
    scheme, _, param = auth_header.partition(" ")
    if scheme.lower() != "bearer":
        raise BearerTokenNotFoundError
    return param
