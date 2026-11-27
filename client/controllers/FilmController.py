from typing import Any, Dict, List, Optional

from flask import (
    Blueprint,
    flash,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from werkzeug.datastructures import MultiDict

from exceptions import USER_INPUT_ERRORS
from services import (
    ActorService,
    ClassificationService,
    DirectorService,
    FilmService,
    GenreService,
    LanguageService,
    LoanService,
    SupportTypeService,
)


def _formToPrefill(form: MultiDict, idFilm: Optional[str] = None) -> Dict[str, Any]:
    """Reconstruit de quoi préremplir films/form.html après une saisie invalide."""

    def reference(
        key: str, nestedKey: str, labelKey: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        value = form.get(key)
        if not value:
            return None
        item = {nestedKey: value}
        if labelKey:
            item["displayName"] = form.get(labelKey, "")
        return item

    def selectedItems(
        key: str, labelKey: str, idKey: str
    ) -> List[Dict[str, Any]]:
        identifiers = form.getlist(key)
        labels = form.getlist(labelKey)
        count = max(len(identifiers), len(labels))
        return [
            {
                idKey: identifiers[index] if index < len(identifiers) else "",
                "displayName": labels[index] if index < len(labels) else "",
            }
            for index in range(count)
            if index < len(identifiers) and identifiers[index]
        ]

    supportFields = [
        form.getlist("supportIds"),
        form.getlist("supportTypeIds"),
        form.getlist("supportLocations"),
        form.getlist("supportUrls"),
    ]
    supportCount = max(map(len, supportFields), default=0)
    return {
        "idFilm": idFilm or form.get("idFilm", ""),
        "title": form.get("title", ""),
        "synopsis": form.get("synopsis", ""),
        "releaseDate": form.get("releaseDate", ""),
        "duration": form.get("duration", ""),
        "posterUrl": form.get("posterUrl", ""),
        "addedDate": form.get("addedDate", ""),
        "director": reference("idDirector", "idDirector", "idDirectorLabels"),
        "classification": reference("idClassification", "idClassification"),
        "nativeLanguage": reference(
            "idNativeLanguage", "idLanguage", "idNativeLanguageLabels"
        ),
        "languages": selectedItems(
            "idLanguages", "idLanguagesLabels", "idLanguage"
        ),
        "genre": [{"idGenre": value} for value in form.getlist("idGenres")],
        "actors": selectedItems("idActors", "idActorsLabels", "idActor"),
        "supports": [
            {
                "idSupport": idSupport or None,
                "idSupportType": idSupportType,
                "location": location,
                "url": url,
            }
            for idSupport, idSupportType, location, url in (
                tuple(values[index] if index < len(values) else "" for values in supportFields)
                for index in range(supportCount)
            )
        ],
    }


def createFilmBlueprint(
    filmService: FilmService,
    directorService: DirectorService,
    genreService: GenreService,
    languageService: LanguageService,
    classificationService: ClassificationService,
    actorService: ActorService,
    supportTypeService: SupportTypeService,
    loanService: LoanService,
) -> Blueprint:
    blueprint = Blueprint("films", __name__, url_prefix="/films")

    def formLists() -> Dict[str, Any]:
        return {
            "classifications": classificationService.getAllClassifications(),
            "genres": genreService.getAllGenres(),
            "supportTypes": supportTypeService.getAllSupportTypes(),
        }

    @blueprint.get("")
    def getFilms():
        title = request.args.get("title")
        idGenre = request.args.get("genre", type=int)
        idDirector = request.args.get("director", type=int)
        idLanguage = request.args.get("language", type=int)
        idActor = request.args.get("actor", type=int)
        idSupportType = request.args.get("supportType", type=int)
        films = filmService.searchFilms(
            title, idGenre, idDirector, idLanguage, idActor, idSupportType
        )
        selectedDirector = (
            directorService.getDirectorById(idDirector)
            if idDirector is not None
            else None
        )
        selectedLanguage = (
            languageService.getLanguageById(idLanguage)
            if idLanguage is not None
            else None
        )
        selectedActor = (
            actorService.getActorById(idActor) if idActor is not None else None
        )
        return render_template(
            "films/list.html",
            films=films,
            genres=genreService.getAllGenres(),
            selectedDirector=selectedDirector,
            selectedLanguage=selectedLanguage,
            selectedActor=selectedActor,
            supportTypes=supportTypeService.getAllSupportTypes(),
            filters={
                "title": title,
                "genre": idGenre,
                "director": idDirector,
                "language": idLanguage,
                "actor": idActor,
                "supportType": idSupportType,
            },
        )

    @blueprint.get("/<string:idFilm>")
    def getFilm(idFilm: str):
        film = filmService.getFilmById(idFilm)
        userLoansBySupport = {}
        if session.get("accessToken") and any(
            support.isAvailable is False for support in film.supports
        ):
            if session.get("user", {}).get("role") in {
                "manager",
                "adminstrateur",
            }:
                userLoansBySupport = loanService.getAllActiveLoansBySupport()
            else:
                userLoansBySupport = loanService.getMyActiveLoansBySupport()
        return render_template(
            "films/detail.html",
            film=film,
            userLoansBySupport=userLoansBySupport,
        )

    @blueprint.route("/new", methods=["GET", "POST"])
    def newFilm():
        prefill = None
        redirectTo = None
        if request.method == "POST":
            try:
                film = filmService.createFilmFromForm(request.form)
                flash("Film ajouté au catalogue.", "success")
                redirectTo = (
                    url_for("films.getFilm", idFilm=film.idFilm)
                    if film
                    else url_for("films.getFilms")
                )
            except USER_INPUT_ERRORS as error:
                flash(str(error), "error")
                prefill = _formToPrefill(request.form)
        response = (
            redirect(redirectTo)
            if redirectTo
            else render_template("films/form.html", film=prefill, isEdit=False, **formLists())
        )
        return response

    @blueprint.route("/<string:idFilm>/edit", methods=["GET", "POST"])
    def editFilm(idFilm: str):
        existingFilm = filmService.getFilmById(idFilm)
        prefill: Any = existingFilm
        redirectTo = None
        if request.method == "POST":
            try:
                film = filmService.updateFilmFromForm(existingFilm, request.form)
                flash("Film modifié.", "success")
                redirectTo = url_for("films.getFilm", idFilm=film.idFilm)
            except USER_INPUT_ERRORS as error:
                flash(str(error), "error")
                prefill = _formToPrefill(request.form, idFilm)
        response = (
            redirect(redirectTo)
            if redirectTo
            else render_template("films/form.html", film=prefill, isEdit=True, **formLists())
        )
        return response

    @blueprint.post("/<string:idFilm>/delete")
    def deleteFilm(idFilm: str):
        filmService.deleteFilm(idFilm)
        flash("Film supprimé.", "success")
        return redirect(url_for("films.getFilms"))

    return blueprint