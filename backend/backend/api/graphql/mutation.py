import strawberry

from backend.services.user.resolvers import create_user_resolver
from backend.services.user.types import CreateUserResponse


@strawberry.type
class Mutation:
    create_user: CreateUserResponse = strawberry.field(resolver=create_user_resolver)
