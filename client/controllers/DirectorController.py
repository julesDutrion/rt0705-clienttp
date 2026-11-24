from flask import Blueprint, flash, redirect, render_template, request, url_for

from exceptions import USER_INPUT_ERRORS
from services import DirectorService

_COLUMNS = [
    {"label": "Identifiant", "key": "idDirector"},
    {"label": "Nom", "key": "lastName"},
    {"label": "Prénom", "key": "firstName"},
]
_FIELDS = [
    {"name": "idDirector", "label": "Identifiant", "type": "number"},
    {"name": "lastName", "label": "Nom"},
    {"name": "firstName", "label": "Prénom"},
]


def createDirectorBlueprint(directorService: DirectorService) -> Blueprint:
    blueprint = Blueprint("directors", __name__, url_prefix="/directors")

    @blueprint.get("")
    def getDirectors():
        return render_template(
            "reference/list.html",
            title="Réalisateurs",
            items=directorService.getAllDirectors(),
            columns=_COLUMNS,
            filterParam="director",
            idKey="idDirector",
            createEndpoint="directors.newDirector",
        )

    @blueprint.route("/new", methods=["GET", "POST"])
    def newDirector():
        values = None
        redirectTo = None
        if request.method == "POST":
            try:
                directorService.createDirectorFromForm(request.form)
                flash("Réalisateur ajouté.", "success")
                redirectTo = url_for("directors.getDirectors")
            except USER_INPUT_ERRORS as error:
                flash(str(error), "error")
                values = request.form
        response = (
            redirect(redirectTo)
            if redirectTo
            else render_template(
                "reference/form.html",
                title="Ajouter un réalisateur",
                fields=_FIELDS,
                values=values,
                cancelEndpoint="directors.getDirectors",
                isEdit=False,
            )
        )
        return response

    @blueprint.route("/<int:idDirector>/edit", methods=["GET", "POST"])
    def editDirector(idDirector: int):
        existing = directorService.getDirectorById(idDirector)
        values = existing
        redirectTo = None
        if request.method == "POST":
            try:
                directorService.updateDirectorFromForm(existing, request.form)
                flash("Réalisateur modifié.", "success")
                redirectTo = url_for("directors.getDirectors")
            except USER_INPUT_ERRORS as error:
                flash(str(error), "error")
                values = request.form
        return (
            redirect(redirectTo)
            if redirectTo
            else render_template(
                "reference/form.html",
                title="Modifier un réalisateur",
                fields=_FIELDS,
                values=values,
                cancelEndpoint="directors.getDirectors",
                isEdit=True,
            )
        )

    @blueprint.post("/<int:idDirector>/delete")
    def deleteDirector(idDirector: int):
        directorService.deleteDirector(idDirector)
        flash("Réalisateur supprimé.", "success")
        return redirect(url_for("directors.getDirectors"))

    return blueprint