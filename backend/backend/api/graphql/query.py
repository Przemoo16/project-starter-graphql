import strawberry

from backend.services.user.resolvers.user import get_me_resolver
from backend.services.user.types.user import User


@strawberry.type
class Query:
    me: User = strawberry.field(resolver=get_me_resolver)
