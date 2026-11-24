from flask import Blueprint, flash, redirect, render_template, request, url_for

from exceptions import USER_INPUT_ERRORS
from services import GenreService

_COLUMNS = [
    {"label": "Identifiant", "key": "idGenre"},
    {"label": "Nom", "key": "nameGenre"},
]
_FIELDS = [
    {"name": "idGenre", "label": "Identifiant", "type": "number"},
    {"name": "nameGenre", "label": "Nom"},
]


def createGenreBlueprint(genreService: GenreService) -> Blueprint:
    blueprint = Blueprint("genres", __name__, url_prefix="/genres")

    @blueprint.get("")
    def getGenres():
        return render_template(
            "reference/list.html",
            title="Genres",
            items=genreService.getAllGenres(),
            columns=_COLUMNS,
            filterParam="genre",
            idKey="idGenre",
            createEndpoint="genres.newGenre",
        )

    @blueprint.route("/new", methods=["GET", "POST"])
    def newGenre():
        values = None
        redirectTo = None
        if request.method == "POST":
            try:
                genreService.createGenreFromForm(request.form)
                flash("Genre ajouté.", "success")
                redirectTo = url_for("genres.getGenres")
            except USER_INPUT_ERRORS as error:
                flash(str(error), "error")
                values = request.form
        response = (
            redirect(redirectTo)
            if redirectTo
            else render_template(
                "reference/form.html",
                title="Ajouter un genre",
                fields=_FIELDS,
                values=values,
                cancelEndpoint="genres.getGenres",
                isEdit=False,
            )
        )
        return response

    @blueprint.route("/<int:idGenre>/edit", methods=["GET", "POST"])
    def editGenre(idGenre: int):
        existing = genreService.getGenreById(idGenre)
        values = existing
        redirectTo = None
        if request.method == "POST":
            try:
                genreService.updateGenreFromForm(existing, request.form)
                flash("Genre modifié.", "success")
                redirectTo = url_for("genres.getGenres")
            except USER_INPUT_ERRORS as error:
                flash(str(error), "error")
                values = request.form
        return (
            redirect(redirectTo)
            if redirectTo
            else render_template(
                "reference/form.html",
                title="Modifier un genre",
                fields=_FIELDS,
                values=values,
                cancelEndpoint="genres.getGenres",
                isEdit=True,
            )
        )

    @blueprint.post("/<int:idGenre>/delete")
    def deleteGenre(idGenre: int):
        genreService.deleteGenre(idGenre)
        flash("Genre supprimé.", "success")
        return redirect(url_for("genres.getGenres"))

    return blueprint