from hashlib import blake2b
from typing import Any


def generate_hash(*args: Any, digest_size: int = 64) -> str:
    hash_algorithm = blake2b(digest_size=digest_size)
    for arg in args:
        hash_algorithm.update(repr(arg).encode())
    return hash_algorithm.hexdigest()
