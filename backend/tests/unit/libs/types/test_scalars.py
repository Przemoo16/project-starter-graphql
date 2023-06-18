from typing import Any

import pytest

from backend.libs.types.scalars import UNSET, is_value_set


@pytest.mark.parametrize(("value", "is_set"), [("test", True), (UNSET, False)])
def test_set_value(value: Any, is_set: bool) -> None:
    res = is_value_set(value)

    assert res == is_set
