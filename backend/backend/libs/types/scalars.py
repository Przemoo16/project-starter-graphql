from typing import Any

import strawberry

UNSET = strawberry.UNSET


def is_value_set(value: Any) -> bool:
    return value is not UNSET
