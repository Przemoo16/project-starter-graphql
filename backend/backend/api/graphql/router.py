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


class Router(GraphQLRouter[Any, None]):
    def encode_json(self, response_data: GraphQLHTTPResponse) -> str:
        return orjson.dumps(response_data).decode()


def get_router(debug: bool = False) -> Router:
    schema = get_schema(debug)
    return Router(schema, graphiql=debug, context_getter=get_context)


def get_schema(debug: bool = False) -> Schema:
    schema_extensions: list[SchemaExtension] = []
    if not debug:
        schema_extensions.append(AddValidationRules([NoSchemaIntrospectionCustomRule]))

    return Schema(query=Query, mutation=Mutation, extensions=schema_extensions)
