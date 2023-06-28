class UserAlreadyExistsError(Exception):
    pass


class UserNotFoundError(Exception):
    pass


class InactiveUserError(Exception):
    pass


class InvalidCredentialsError(Exception):
    pass
