import strawberry


@strawberry.type
class UserCreate:
    email: str
    password: str
    full_name: str


@strawberry.type
class UserUpdate:
    pass


@strawberry.type
class UserFilters:
    pass
