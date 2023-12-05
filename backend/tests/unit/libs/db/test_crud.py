from typing import Any

import pytest

from backend.libs.db.crud import UNSET, UnsetType, is_unset


def test_unset_type_is_singleton() -> None:
    object_1 = UnsetType()
    object_2 = UnsetType()

    assert object_1 is object_2


@pytest.mark.parametrize(("value", "expected"), [(UNSET, True), (None, False)])
def test_is_unset_indicates_if_value_is_unset(value: Any, expected: bool) -> None:
    unset = is_unset(value)

    assert unset == expected
