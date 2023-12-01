from typing import Any

from sqlalchemy.ext.compiler import compiles
from sqlalchemy.sql import expression
from sqlalchemy.types import DateTime


class utcnow(expression.FunctionElement[Any]):  # noqa: N801
    type = DateTime()
    inherit_cache = True


@compiles(utcnow, "postgresql")  # type: ignore[no-untyped-call, misc]
def pg_utcnow(  # type: ignore[no-untyped-def]
    element, compiler, **kw  # noqa: ARG001
) -> str:
    return "TIMEZONE('utc', CURRENT_TIMESTAMP)"
