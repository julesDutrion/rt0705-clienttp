"""Racine de composition du client : assemble les dépendances et crée l'application Flask."""

from flask import Flask, redirect, url_for

from config import API_BASE_URL, API_TIMEOUT, CLIENT_DEBUG, CLIENT_HOST, CLIENT_PORT, SECRET_KEY
from controllers import (
    createClassificationBlueprint,
    createDirectorBlueprint,
    createFilmBlueprint,
    createGenreBlueprint,
    createLanguageBlueprint,
    createActorBlueprint,
    createSupportTypeBlueprint,
)
from ErrorHandlers import registerErrorHandlers
from services import (
    ApiClient,
    ClassificationService,
    DirectorService,
    FilmService,
    GenreService,
    LanguageService,
    ActorService,
    SupportService,
    SupportTypeService,
)


def createApp() -> Flask:
    app = Flask(__name__, template_folder="view/templates", static_folder="view/static")
    app.config["SECRET_KEY"] = SECRET_KEY

    # Services : ils parlent à l'API via un unique ApiClient
    apiClient = ApiClient(API_BASE_URL, API_TIMEOUT)
    directorService = DirectorService(apiClient)
    genreService = GenreService(apiClient)
    languageService = LanguageService(apiClient)
    classificationService = ClassificationService(apiClient)
    actorService = ActorService(apiClient)
    supportService = SupportService(apiClient)
    supportTypeService = SupportTypeService(apiClient)
    filmService = FilmService(
        apiClient,
        genreService,
        classificationService,
        actorService,
        supportService,
        supportTypeService,
    )

    # Contrôleurs
    app.register_blueprint(createFilmBlueprint(
        filmService,
        directorService,
        genreService,
        languageService,
        classificationService,
        actorService,
        supportTypeService,
    ))
    app.register_blueprint(createActorBlueprint(actorService))
    app.register_blueprint(createDirectorBlueprint(directorService))
    app.register_blueprint(createGenreBlueprint(genreService))
    app.register_blueprint(createLanguageBlueprint(languageService))
    app.register_blueprint(createClassificationBlueprint(classificationService))
    app.register_blueprint(createSupportTypeBlueprint(supportTypeService))

    @app.get("/")
    def index():
        return redirect(url_for("films.getFilms"))

    # TEMPORAIRE, avant l'authentification : pour voir l'interface « publication » dans les templates.
    # app.context_processor(lambda: {"canPublish": True})

    registerErrorHandlers(app)
    return app


if __name__ == "__main__":
    createApp().run(host=CLIENT_HOST, port=CLIENT_PORT, debug=CLIENT_DEBUG)