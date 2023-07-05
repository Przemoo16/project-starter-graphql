import strawberry

from backend.services.user.resolvers import (
    confirm_email_resolver,
    create_user_resolver,
    login_resolver,
)
from backend.services.user.types import (
    ConfirmEmailResponse,
    CreateUserResponse,
    LoginResponse,
)


@strawberry.type
class Mutation:
    create_user: CreateUserResponse = strawberry.field(resolver=create_user_resolver)
    confirm_email: ConfirmEmailResponse = strawberry.field(
        resolver=confirm_email_resolver
    )
    login: LoginResponse = strawberry.field(resolver=login_resolver)
