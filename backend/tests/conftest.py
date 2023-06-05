import pytest


@pytest.fixture(name="anyio_backend", scope="session")
def anyio_backend_fixture() -> str:
    return "asyncio"
