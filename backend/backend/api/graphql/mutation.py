import strawberry

from backend.api.graphql.resolvers.user import create_user_resolver
from backend.api.graphql.types.user import CreateUserResponse


@strawberry.type
class Mutation:
    create_user: CreateUserResponse = strawberry.field(resolver=create_user_resolver)
