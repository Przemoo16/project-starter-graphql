import strawberry


@strawberry.interface
class Problem:
    message: str
