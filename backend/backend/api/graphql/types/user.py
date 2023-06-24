from uuid import UUID

import strawberry

from backend.api.graphql.types.error import Failure


@strawberry.input
class UserCreateInput:
    email: str
    password: str


@strawberry.type
class User:
    id: UUID
    email: str


@strawberry.type
class UserAlreadyExists(Failure):
    message: str = "User with provided email already exists"
    email: str


CreateUserResponse = User | UserAlreadyExists
