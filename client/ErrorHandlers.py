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
    def errorPage(code: int, message: str):
        return render_template("errors/error.html", code=code, message=message), code

    @app.errorhandler(AuthenticationError)
    def handleAuthenticationError(error: AuthenticationError):
        session.clear()
        flash("Votre session a expiré. Veuillez vous reconnecter.", "error")
        return redirect(url_for("account.login"))

    @app.errorhandler(ForbiddenError)
    def handleForbidden(error: ForbiddenError):
        return errorPage(403, "Vous n'avez pas les droits nécessaires.")

    @app.errorhandler(403)
    def handleForbiddenHttp(error):
        return errorPage(403, "Vous n'avez pas les droits nécessaires.")

    @app.errorhandler(NotFoundError)
    def handleNotFound(error: NotFoundError):
        return errorPage(404, "Ressource introuvable.")

    @app.errorhandler(InvalidRequestError)
    def handleInvalidRequest(error: InvalidRequestError):
        return errorPage(400, "Requête invalide.")

    @app.errorhandler(AlreadyExistsError)
    def handleAlreadyExists(error: AlreadyExistsError):
        return errorPage(409, "Cet élément existe déjà.")

    @app.errorhandler(InvalidReferenceError)
    def handleInvalidReference(error: InvalidReferenceError):
        return errorPage(422, "Un élément référencé n'existe pas.")

    @app.errorhandler(ApiUnavailableError)
    def handleApiUnavailable(error: ApiUnavailableError):
        app.logger.error("API unavailable: %s", error)
        return errorPage(503, "Le service distant est momentanément indisponible.")

    @app.errorhandler(ApiError)
    def handleApiError(error: ApiError):
        app.logger.error("API error: %s", error)
        return errorPage(502, "Réponse inattendue du service distant.")

    @app.errorhandler(HTTPException)
    def handleHttpException(error: HTTPException):
        message = "Page introuvable." if error.code == 404 else error.description
        return errorPage(error.code or 500, message)

    @app.errorhandler(Exception)
    def handleUnexpectedError(error: Exception):
        app.logger.exception("Unhandled exception")
        return errorPage(500, "Une erreur interne est survenue.")