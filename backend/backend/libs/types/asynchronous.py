from collections.abc import Callable
from typing import ParamSpec, Protocol, TypeVar

T = TypeVar("T")
P = ParamSpec("P")


class AsyncExecutor(Protocol):
    async def __call__(
        self, func: Callable[P, T], *args: P.args, **kwargs: P.kwargs
    ) -> T:
        ...
