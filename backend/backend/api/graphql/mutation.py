import strawberry

from backend.services.user.resolvers.auth import login_resolver
from backend.services.user.resolvers.email import confirm_email_resolver
from backend.services.user.resolvers.password import (
    reset_password_resolver,
    set_password_resolver,
)
from backend.services.user.resolvers.user import create_user_resolver
from backend.services.user.types.auth import LoginResponse
from backend.services.user.types.email import ConfirmEmailResponse
from backend.services.user.types.password import (
    ResetPasswordResponse,
    SetPasswordResponse,
)
from backend.services.user.types.user import CreateUserResponse


@strawberry.type
class Mutation:
    create_user: CreateUserResponse = strawberry.field(resolver=create_user_resolver)
    confirm_email: ConfirmEmailResponse = strawberry.field(
        resolver=confirm_email_resolver
    )
    login: LoginResponse = strawberry.field(resolver=login_resolver)
    reset_password: ResetPasswordResponse = strawberry.field(
        resolver=reset_password_resolver
    )
    set_password: SetPasswordResponse = strawberry.field(resolver=set_password_resolver)
