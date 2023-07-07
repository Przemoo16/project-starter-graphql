from dataclasses import dataclass


class UserAlreadyExistsError(Exception):
    pass


class UserNotFoundError(Exception):
    pass


class UserNotConfirmedError(Exception):
    pass


class InvalidEmailConfirmationTokenError(Exception):
    pass


@dataclass
class UserAlreadyConfirmedError(Exception):
    email: str


class InvalidCredentialsError(Exception):
    pass


class InvalidResetPasswordTokenError(Exception):
    pass
