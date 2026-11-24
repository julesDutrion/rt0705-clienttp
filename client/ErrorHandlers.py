"""Traduction des exceptions en pages d'erreur."""

from flask import Flask, render_template
from werkzeug.exceptions import HTTPException

from exceptions import (
    AlreadyExistsError,
    ApiError,
    ApiUnavailableError,
    InvalidReferenceError,
    InvalidRequestError,
    NotFoundError,
)


def registerErrorHandlers(app: Flask) -> None:
    def errorPage(code: int, message: str):
        return render_template("errors/error.html", code=code, message=message), code

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
        return errorPage(503, "Le service de catalogue est momentanément indisponible.")

    @app.errorhandler(ApiError)
    def handleApiError(error: ApiError):
        app.logger.error("API error: %s", error)
        return errorPage(502, "Réponse inattendue du service de catalogue.")

    @app.errorhandler(HTTPException)
    def handleHttpException(error: HTTPException):
        message = "Page introuvable." if error.code == 404 else error.description
        return errorPage(error.code or 500, message)

    @app.errorhandler(Exception)
    def handleUnexpectedError(error: Exception):
        app.logger.exception("Unhandled exception")
        return errorPage(500, "Une erreur interne est survenue.")