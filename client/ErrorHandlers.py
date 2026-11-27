"""Traduction des exceptions en pages d'erreur."""

from flask import Flask, flash, redirect, render_template, session, url_for
from werkzeug.exceptions import HTTPException

from exceptions import (
    AlreadyExistsError,
    ApiError,
    ApiUnavailableError,
    AuthenticationError,
    ForbiddenError,
    InvalidReferenceError,
    InvalidRequestError,
    NotFoundError,
)


def registerErrorHandlers(app: Flask) -> None:
    """
    Méthode qui enregistre les gestionnaires d'erreurs Flask.

    :param app: Application Flask à configurer.
    """

    def errorPage(code: int, message: str):
        """
        Méthode qui construit une page d'erreur HTTP.

        :param code: Code HTTP de l'erreur.
        :param message: Message à afficher.
        :return: Réponse Flask et code HTTP.
        """
        return render_template("errors/error.html", code=code, message=message), code

    @app.errorhandler(AuthenticationError)
    def handleAuthenticationError(error: AuthenticationError):
        """
        Méthode qui traite une erreur d'authentification.

        :param error: Erreur d'authentification reçue.
        :return: Redirection vers la connexion.
        """
        session.clear()
        flash("Votre session a expiré. Veuillez vous reconnecter.", "error")
        return redirect(url_for("account.login"))

    @app.errorhandler(ForbiddenError)
    def handleForbidden(error: ForbiddenError):
        """
        Méthode qui traite un refus d'autorisation.

        :param error: Erreur d'autorisation reçue.
        :return: Page d'erreur 403.
        """
        return errorPage(403, "Vous n'avez pas les droits nécessaires.")

    @app.errorhandler(403)
    def handleForbiddenHttp(error):
        """
        Méthode qui traite un refus HTTP 403.

        :param error: Erreur HTTP reçue.
        :return: Page d'erreur 403.
        """
        return errorPage(403, "Vous n'avez pas les droits nécessaires.")

    @app.errorhandler(NotFoundError)
    def handleNotFound(error: NotFoundError):
        """
        Méthode qui traite une ressource introuvable.

        :param error: Erreur de ressource introuvable.
        :return: Page d'erreur 404.
        """
        return errorPage(404, "Ressource introuvable.")

    @app.errorhandler(InvalidRequestError)
    def handleInvalidRequest(error: InvalidRequestError):
        """
        Méthode qui traite une requête invalide.

        :param error: Erreur de requête reçue.
        :return: Page d'erreur 400.
        """
        return errorPage(400, "Requête invalide.")

    @app.errorhandler(AlreadyExistsError)
    def handleAlreadyExists(error: AlreadyExistsError):
        """
        Méthode qui traite un conflit de ressource.

        :param error: Erreur de conflit reçue.
        :return: Page d'erreur 409.
        """
        return errorPage(409, "Cet élément existe déjà.")

    @app.errorhandler(InvalidReferenceError)
    def handleInvalidReference(error: InvalidReferenceError):
        """
        Méthode qui traite une référence invalide.

        :param error: Erreur de référence reçue.
        :return: Page d'erreur 422.
        """
        return errorPage(422, "Un élément référencé n'existe pas.")

    @app.errorhandler(ApiUnavailableError)
    def handleApiUnavailable(error: ApiUnavailableError):
        """
        Méthode qui traite une indisponibilité de l'API.

        :param error: Erreur d'indisponibilité reçue.
        :return: Page d'erreur 503.
        """
        app.logger.error("API unavailable: %s", error)
        return errorPage(503, "Le service distant est momentanément indisponible.")

    @app.errorhandler(ApiError)
    def handleApiError(error: ApiError):
        """
        Méthode qui traite une erreur de réponse de l'API.

        :param error: Erreur API reçue.
        :return: Page d'erreur 502.
        """
        app.logger.error("API error: %s", error)
        return errorPage(502, "Réponse inattendue du service distant.")

    @app.errorhandler(HTTPException)
    def handleHttpException(error: HTTPException):
        """
        Méthode qui traite une erreur HTTP Flask.

        :param error: Erreur HTTP reçue.
        :return: Page d'erreur correspondant au statut HTTP.
        """
        message = "Page introuvable." if error.code == 404 else error.description
        return errorPage(error.code or 500, message)

    @app.errorhandler(Exception)
    def handleUnexpectedError(error: Exception):
        """
        Méthode qui traite une erreur inattendue.

        :param error: Exception reçue.
        :return: Page d'erreur 500.
        """
        app.logger.exception("Unhandled exception")
        return errorPage(500, "Une erreur interne est survenue.")