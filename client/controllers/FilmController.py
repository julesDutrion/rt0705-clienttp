from typing import Any, Dict, Optional

from flask import Blueprint, flash, redirect, render_template, request, url_for
from werkzeug.datastructures import MultiDict

from exceptions import USER_INPUT_ERRORS
from services import (
    ActorService,
    ClassificationService,
    DirectorService,
    FilmService,
    GenreService,
    LanguageService,
    SupportTypeService,
)


def _formToPrefill(form: MultiDict, idFilm: Optional[str] = None) -> Dict[str, Any]:
    """Reconstruit de quoi préremplir films/form.html après une saisie invalide."""

    def reference(key: str, nestedKey: str) -> Optional[Dict[str, Any]]:
        value = form.get(key)
        return {nestedKey: value} if value else None

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
        "director": reference("idDirector", "idDirector"),
        "classification": reference("idClassification", "idClassification"),
        "nativeLanguage": reference("idNativeLanguage", "idLanguage"),
        "languages": [{"idLanguage": value} for value in form.getlist("idLanguages")],
        "genre": [{"idGenre": value} for value in form.getlist("idGenres")],
        "actors": [{"idActor": value} for value in form.getlist("idActors")],
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
) -> Blueprint:
    blueprint = Blueprint("films", __name__, url_prefix="/films")

    def formLists() -> Dict[str, Any]:
        return {
            "directors": directorService.getAllDirectors(),
            "classifications": classificationService.getAllClassifications(),
            "languages": languageService.getAllLanguages(),
            "genres": genreService.getAllGenres(),
            "actors": actorService.getAllActors(),
            "supportTypes": supportTypeService.getAllSupportTypes(),
        }

    @blueprint.get("")
    def getFilms():
        title = request.args.get("title")
        idGenre = request.args.get("genre", type=int)
        idDirector = request.args.get("director", type=int)
        idLanguage = request.args.get("language", type=int)
        idActor = request.args.get("actor", type=int)
        films = filmService.searchFilms(
            title, idGenre, idDirector, idLanguage, idActor
        )
        return render_template(
            "films/list.html",
            films=films,
            genres=genreService.getAllGenres(),
            directors=directorService.getAllDirectors(),
            languages=languageService.getAllLanguages(),
            actors=actorService.getAllActors(),
            filters={
                "title": title,
                "genre": idGenre,
                "director": idDirector,
                "language": idLanguage,
                "actor": idActor,
            },
        )

    @blueprint.get("/<string:idFilm>")
    def getFilm(idFilm: str):
        film = filmService.getFilmById(idFilm)
        return render_template("films/detail.html", film=film)

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