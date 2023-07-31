import strawberry

from backend.services.user.resolvers.auth import login_resolver, refresh_token_resolver
from backend.services.user.resolvers.email import confirm_email_resolver
from backend.services.user.resolvers.password import (
    change_my_password_resolver,
    recover_password_resolver,
    reset_password_resolver,
)
from backend.services.user.resolvers.user import (
    create_user_resolver,
    delete_me_resolver,
    update_me_resolver,
)
from backend.services.user.types.auth import LoginResponse, RefreshTokenResponse
from backend.services.user.types.email import ConfirmEmailResponse
from backend.services.user.types.password import (
    ChangeMyPasswordResponse,
    RecoverPasswordResponse,
    ResetPasswordResponse,
)
from backend.services.user.types.user import (
    CreateUserResponse,
    DeleteMeResponse,
    UpdateMeResponse,
)


@strawberry.type
class Mutation:
    create_user: CreateUserResponse = strawberry.field(resolver=create_user_resolver)
    update_me: UpdateMeResponse = strawberry.field(resolver=update_me_resolver)
    delete_me: DeleteMeResponse = strawberry.field(resolver=delete_me_resolver)
    confirm_email: ConfirmEmailResponse = strawberry.field(
        resolver=confirm_email_resolver
    )
    login: LoginResponse = strawberry.field(resolver=login_resolver)
    recover_password: RecoverPasswordResponse = strawberry.field(
        resolver=recover_password_resolver
    )
    reset_password: ResetPasswordResponse = strawberry.field(
        resolver=reset_password_resolver
    )
    change_my_password: ChangeMyPasswordResponse = strawberry.field(
        resolver=change_my_password_resolver
    )
    refresh_token: RefreshTokenResponse = strawberry.field(
        resolver=refresh_token_resolver
    )
