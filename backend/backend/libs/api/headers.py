from collections.abc import Mapping


class BearerTokenNotFoundError(Exception):
    pass


def read_bearer_token(headers: Mapping[str, str]) -> str:
    auth_header = headers.get("Authentication")
    if not auth_header:
        raise BearerTokenNotFoundError
    scheme, _, param = auth_header.partition(" ")
    if scheme.lower() != "bearer":
        raise BearerTokenNotFoundError
    return param
