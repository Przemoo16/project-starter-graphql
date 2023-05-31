from typing import Any

from sqlalchemy.ext.compiler import compiles
from sqlalchemy.sql import expression
from sqlalchemy.types import DateTime


class utcnow(  # pylint: disable=invalid-name, abstract-method, too-many-ancestors
    expression.FunctionElement[Any]
):
    type = DateTime()
    inherit_cache = True


@compiles(utcnow, "postgresql")  # type: ignore[no-untyped-call, misc]
def pg_utcnow(  # type: ignore[no-untyped-def] # pylint: disable=unused-argument
    element, compiler, **kw
) -> str:
    return "TIMEZONE('utc', CURRENT_TIMESTAMP)"