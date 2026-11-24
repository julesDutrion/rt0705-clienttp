class ClientError(Exception):
    pass


class ApiError(ClientError):
    pass


class ApiUnavailableError(ApiError):
    pass


class InvalidRequestError(ClientError):
    pass


class InvalidReferenceError(ClientError):
    pass


class AlreadyExistsError(ClientError):
    pass


class NotFoundError(ClientError):
    pass


USER_INPUT_ERRORS = (
    InvalidRequestError,
    InvalidReferenceError,
    AlreadyExistsError,
)