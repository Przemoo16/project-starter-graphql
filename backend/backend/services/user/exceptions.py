class UserAlreadyExistsError(Exception):
    pass


class UserNotFoundError(Exception):
    pass


class UserNotConfirmedError(Exception):
    pass


class InvalidEmailConfirmationTokenError(Exception):
    pass


class UserAlreadyConfirmedError(Exception):
    pass


class InvalidCredentialsError(Exception):
    pass


class InvalidResetPasswordTokenError(Exception):
    pass
