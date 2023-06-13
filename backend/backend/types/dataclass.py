from typing import Any, ClassVar, Protocol


class DataClassProtocol(Protocol):
    __dataclass_fields__: ClassVar[dict[str, Any]]
