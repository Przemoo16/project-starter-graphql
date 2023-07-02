class UserAlreadyExistsError(Exception):
    pass


class UserNotFoundError(Exception):
    pass


class UserNotConfirmedError(Exception):
    pass


class InvalidCredentialsError(Exception):
    pass
