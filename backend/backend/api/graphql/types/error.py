import strawberry


@strawberry.interface
class Failure:
    message: str
