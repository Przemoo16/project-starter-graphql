import strawberry

from backend.libs.api.types import User
from backend.services.user.resolvers.user import get_me_resolver


@strawberry.type
class Query:
    me: User = strawberry.field(resolver=get_me_resolver)
