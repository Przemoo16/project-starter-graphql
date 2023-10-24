from collections.abc import Callable
from typing import ParamSpec, TypeVar

T = TypeVar("T")
P = ParamSpec("P")


async def run_without_executor(
    func: Callable[P, T], *args: P.args, **kwargs: P.kwargs
) -> T:
    return func(*args, **kwargs)
