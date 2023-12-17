from typing import Any, Optional


class UnsetType:
    __instance: Optional["UnsetType"] = None

    def __new__(cls) -> "UnsetType":
        if not cls.__instance:
            cls.__instance = super().__new__(cls)
        return cls.__instance


UNSET = UnsetType()


def is_unset(value: Any) -> bool:
    return value is UNSET
