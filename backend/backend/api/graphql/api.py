import orjson
import strawberry
from graphql.validation import NoSchemaIntrospectionCustomRule
from strawberry import Schema
from strawberry.extensions import AddValidationRules, SchemaExtension
from strawberry.fastapi import GraphQLRouter
from strawberry.http import GraphQLHTTPResponse


@strawberry.type
class Query:
    test: str


class Router(GraphQLRouter):  # type: ignore[type-arg]
    def encode_json(self, response_data: GraphQLHTTPResponse) -> str:
        return orjson.dumps(response_data).decode()


def get_router(debug: bool = False) -> Router:
    schema = get_schema(debug)
    return Router(schema, graphiql=debug)


def get_schema(debug: bool = False) -> Schema:
    schema_extensions: list[SchemaExtension] = []
    if not debug:
        schema_extensions.append(AddValidationRules([NoSchemaIntrospectionCustomRule]))

    return Schema(Query, extensions=schema_extensions)
