from typing import Any

import pytest

from backend.types.scalars import UNSET, is_unset


@pytest.mark.parametrize("value,unset", [("test", False), (UNSET, True)])
def test_value_is_unset(value: Any, unset: bool) -> None:
    res = is_unset(value)

    assert res == unset
