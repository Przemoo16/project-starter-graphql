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


class InvalidPasswordError(Exception):
    pass


class InvalidResetPasswordTokenError(Exception):
    pass


class InvalidResetPasswordTokenFingerprintError(Exception):
    pass


class MissingAccessTokenError(Exception):
    pass


class InvalidAccessTokenError(Exception):
    pass


class InvalidRefreshTokenError(Exception):
    pass
