from flask import Blueprint, flash, redirect, render_template, request, url_for

from exceptions import USER_INPUT_ERRORS
from services import ActorService

_COLUMNS = [
    {"label": "Identifiant", "key": "idActor"},
    {"label": "Prénom", "key": "firstName"},
    {"label": "Nom", "key": "lastName"},
]
_FIELDS = [
    {"name": "idActor", "label": "Identifiant", "type": "number"},
    {"name": "firstName", "label": "Prénom"},
    {"name": "lastName", "label": "Nom"},
]


def createActorBlueprint(actorService: ActorService) -> Blueprint:
    blueprint = Blueprint("actors", __name__, url_prefix="/actors")

    @blueprint.get("")
    def getActors():
        return render_template(
            "reference/list.html",
            title="Acteurs",
            items=actorService.getAllActors(),
            columns=_COLUMNS,
            filterParam="actor",
            idKey="idActor",
            createEndpoint="actors.newActor",
        )

    @blueprint.route("/new", methods=["GET", "POST"])
    def newActor():
        values = None
        redirectTo = None
        if request.method == "POST":
            try:
                actorService.createActorFromForm(request.form)
                flash("Acteur ajouté.", "success")
                redirectTo = url_for("actors.getActors")
            except USER_INPUT_ERRORS as error:
                flash(str(error), "error")
                values = request.form
        return (
            redirect(redirectTo)
            if redirectTo
            else render_template(
                "reference/form.html",
                title="Ajouter un acteur",
                fields=_FIELDS,
                values=values,
                cancelEndpoint="actors.getActors",
                isEdit=False,
            )
        )

    @blueprint.route("/<int:idActor>/edit", methods=["GET", "POST"])
    def editActor(idActor: int):
        existing = actorService.getActorById(idActor)
        values = existing
        redirectTo = None
        if request.method == "POST":
            try:
                actorService.updateActorFromForm(existing, request.form)
                flash("Acteur modifié.", "success")
                redirectTo = url_for("actors.getActors")
            except USER_INPUT_ERRORS as error:
                flash(str(error), "error")
                values = request.form
        return (
            redirect(redirectTo)
            if redirectTo
            else render_template(
                "reference/form.html",
                title="Modifier un acteur",
                fields=_FIELDS,
                values=values,
                cancelEndpoint="actors.getActors",
                isEdit=True,
            )
        )

    @blueprint.post("/<int:idActor>/delete")
    def deleteActor(idActor: int):
        actorService.deleteActor(idActor)
        flash("Acteur supprimé.", "success")
        return redirect(url_for("actors.getActors"))

    return blueprint
