class ClientError(Exception):
    """Classe qui représente une erreur applicative du client."""


class ApiError(ClientError):
    """Classe qui représente une erreur de réponse de l'API."""


class ApiUnavailableError(ApiError):
    """Classe qui représente une indisponibilité de l'API."""


class AuthenticationError(ClientError):
    """Classe qui représente une erreur d'authentification."""


class ForbiddenError(ClientError):
    """Classe qui représente un refus d'autorisation."""


class InvalidRequestError(ClientError):
    """Classe qui représente une requête invalide."""


class InvalidReferenceError(ClientError):
    """Classe qui représente une référence API invalide."""


class AlreadyExistsError(ClientError):
    """Classe qui représente un conflit avec une ressource existante."""


class NotFoundError(ClientError):
    """Classe qui représente une ressource introuvable."""


USER_INPUT_ERRORS = (
    InvalidRequestError,
    InvalidReferenceError,
    AlreadyExistsError,
)