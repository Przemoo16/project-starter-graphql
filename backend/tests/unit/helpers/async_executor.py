from collections.abc import Callable
from typing import ParamSpec, TypeVar

_T = TypeVar("_T")
_P = ParamSpec("_P")


async def run_without_executor(
    func: Callable[_P, _T], *args: _P.args, **kwargs: _P.kwargs
) -> _T:
    return func(*args, **kwargs)
