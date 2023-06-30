import strawberry

from backend.services.user.resolvers import create_user_resolver, login
from backend.services.user.types import CreateUserResponse, LoginResponse


@strawberry.type
class Mutation:
    create_user: CreateUserResponse = strawberry.field(resolver=create_user_resolver)
    login: LoginResponse = strawberry.field(resolver=login)
