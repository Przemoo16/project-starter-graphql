from typing import Any

import strawberry

UNSET = strawberry.UNSET


def is_unset(value: Any) -> bool:
    return value is UNSET
