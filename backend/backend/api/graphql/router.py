from typing import Any

import orjson
from graphql.validation import NoSchemaIntrospectionCustomRule
from strawberry import Schema
from strawberry.extensions import AddValidationRules, SchemaExtension
from strawberry.fastapi import GraphQLRouter
from strawberry.http import GraphQLHTTPResponse

from backend.api.graphql.context import get_context
from backend.api.graphql.mutation import Mutation
from backend.api.graphql.query import Query


class _Router(GraphQLRouter[Any, None]):
    def encode_json(self, response_data: GraphQLHTTPResponse) -> str:
        return orjson.dumps(response_data).decode()


def get_router(debug: bool = False) -> _Router:
    schema = _get_schema(debug)
    graphql_ide = "graphiql" if debug else None
    return _Router(
        schema,
        graphql_ide=graphql_ide,  # type: ignore[arg-type]
        context_getter=get_context,
    )


def _get_schema(debug: bool = False) -> Schema:
    schema_extensions: list[SchemaExtension] = []
    if not debug:
        schema_extensions.append(AddValidationRules([NoSchemaIntrospectionCustomRule]))

    return Schema(query=Query, mutation=Mutation, extensions=schema_extensions)
