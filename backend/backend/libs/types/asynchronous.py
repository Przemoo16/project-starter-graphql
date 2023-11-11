from collections.abc import Callable
from typing import ParamSpec, Protocol, TypeVar

_T = TypeVar("_T")
_P = ParamSpec("_P")


class AsyncExecutor(Protocol):
    async def __call__(  # pylint: disable=no-member
        self, func: Callable[_P, _T], *args: _P.args, **kwargs: _P.kwargs
    ) -> _T:
        ...
