"""Racine de composition du client : assemble les dépendances et crée l'application Flask."""

from flask import (
    Flask,
    abort,
    flash,
    has_request_context,
    redirect,
    request,
    session,
    url_for,
)

from config import API_BASE_URL, API_TIMEOUT, CLIENT_DEBUG, CLIENT_HOST, CLIENT_PORT, SECRET_KEY
from controllers import (
    createClassificationBlueprint,
    createDirectorBlueprint,
    createFilmBlueprint,
    createGenreBlueprint,
    createLanguageBlueprint,
    createActorBlueprint,
    createAccountBlueprint,
    createSupportTypeBlueprint,
    createLoanBlueprint,
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
    UserService,
    LoanService,
)

MANAGEMENT_PAGE_ENDPOINTS = {
    "getActors",
    "getClassifications",
    "getDirectors",
    "getGenres",
    "getLanguages",
    "getSupportTypes",
    "manageLoans",
    "managedLoanDetail",
    "returnLoan",
}


def createApp() -> Flask:
    app = Flask(__name__, template_folder="view/templates", static_folder="view/static")
    app.config["SECRET_KEY"] = SECRET_KEY

    # Services : ils parlent à l'API via un unique ApiClient
    def currentAccessToken():
        return session.get("accessToken") if has_request_context() else None

    apiClient = ApiClient(
        API_BASE_URL, API_TIMEOUT, accessTokenProvider=currentAccessToken
    )
    directorService = DirectorService(apiClient)
    genreService = GenreService(apiClient)
    languageService = LanguageService(apiClient)
    classificationService = ClassificationService(apiClient)
    actorService = ActorService(apiClient)
    supportService = SupportService(apiClient)
    supportTypeService = SupportTypeService(apiClient)
    userService = UserService(apiClient)
    filmService = FilmService(
        apiClient,
        genreService,
        classificationService,
        actorService,
        supportService,
        supportTypeService,
    )
    loanService = LoanService(
        apiClient, supportService, filmService, userService
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
        loanService,
    ))
    app.register_blueprint(createActorBlueprint(actorService))
    app.register_blueprint(createDirectorBlueprint(directorService))
    app.register_blueprint(createGenreBlueprint(genreService))
    app.register_blueprint(createLanguageBlueprint(languageService))
    app.register_blueprint(createClassificationBlueprint(classificationService))
    app.register_blueprint(createSupportTypeBlueprint(supportTypeService))
    app.register_blueprint(createAccountBlueprint(userService))
    app.register_blueprint(createLoanBlueprint(loanService))

    @app.get("/")
    def index():
        return redirect(url_for("films.getFilms"))

    @app.before_request
    def restrictManagementAccess():
        endpoint = request.endpoint or ""
        routeName = endpoint.rsplit(".", 1)[-1]
        isWriteRoute = routeName.startswith(("new", "edit", "delete"))
        if isWriteRoute or routeName in MANAGEMENT_PAGE_ENDPOINTS:
            if not session.get("accessToken"):
                flash("Connectez-vous pour accéder aux pages de gestion.", "error")
                return redirect(url_for("account.login"))
            role = session.get("user", {}).get("role")
            if role not in {"manager", "adminstrateur"}:
                abort(403)

    @app.context_processor
    def accountContext():
        user = session.get("user")
        role = user.get("role") if user else None
        return {
            "currentUser": user,
            "canPublish": role in {"manager", "adminstrateur"},
            "isAdmin": role == "adminstrateur",
            "canManageLoans": role in {"manager", "adminstrateur"},
        }

    registerErrorHandlers(app)
    return app


if __name__ == "__main__":
    createApp().run(host=CLIENT_HOST, port=CLIENT_PORT, debug=CLIENT_DEBUG)