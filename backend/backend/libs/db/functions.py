from typing import Any

from sqlalchemy.ext.compiler import compiles
from sqlalchemy.sql import expression
from sqlalchemy.types import DateTime


class utcnow(  # noqa: N801 # pylint: disable=invalid-name
    expression.FunctionElement[Any]
):
    type = DateTime()
    inherit_cache = True


@compiles(utcnow, "postgresql")  # type: ignore[no-untyped-call, misc]
def pg_utcnow(  # type: ignore[no-untyped-def] # pylint: disable=unused-argument
    element, compiler, **kw
) -> str:
    return "TIMEZONE('utc', CURRENT_TIMESTAMP)"
