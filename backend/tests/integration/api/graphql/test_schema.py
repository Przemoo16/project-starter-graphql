import pytest

from backend.api.graphql.api import get_schema


@pytest.mark.parametrize("debug,error", [(True, False), (False, True)])
def test_enable_disable_schema_introspection(debug: bool, error: bool) -> None:
    query = """
        query {
            __schema {
                types {
                    name
                }
            }
        }
    """

    result = get_schema(debug).execute_sync(query)

    assert bool(result.errors) == error
