from flask import Blueprint, flash, redirect, render_template, request, url_for

from exceptions import USER_INPUT_ERRORS
from services import ClassificationService

_COLUMNS = [
    {"label": "Identifiant", "key": "idClassification"},
    {"label": "Âge minimum", "key": "minAge"},
]
_FIELDS = [
    {"name": "idClassification", "label": "Identifiant", "type": "number"},
    {"name": "minAge", "label": "Âge minimum (0 = tout public)", "type": "number"},
]


def createClassificationBlueprint(classificationService: ClassificationService) -> Blueprint:
    blueprint = Blueprint("classifications", __name__, url_prefix="/classifications")

    @blueprint.get("")
    def getClassifications():
        # L'API ne permet pas de filtrer les films par classification : pas de lien « Voir les films ».
        return render_template(
            "reference/list.html",
            title="Classifications",
            items=classificationService.getAllClassifications(),
            columns=_COLUMNS,
            createEndpoint="classifications.newClassification",
        )

    @blueprint.route("/new", methods=["GET", "POST"])
    def newClassification():
        values = None
        redirectTo = None
        if request.method == "POST":
            try:
                classificationService.createClassificationFromForm(request.form)
                flash("Classification ajoutée.", "success")
                redirectTo = url_for("classifications.getClassifications")
            except USER_INPUT_ERRORS as error:
                flash(str(error), "error")
                values = request.form
        response = (
            redirect(redirectTo)
            if redirectTo
            else render_template(
                "reference/form.html",
                title="Ajouter une classification",
                fields=_FIELDS,
                values=values,
                cancelEndpoint="classifications.getClassifications",
                isEdit=False,
            )
        )
        return response

    @blueprint.route("/<int:idClassification>/edit", methods=["GET", "POST"])
    def editClassification(idClassification: int):
        existing = classificationService.getClassificationById(idClassification)
        values = existing
        redirectTo = None
        if request.method == "POST":
            try:
                classificationService.updateClassificationFromForm(existing, request.form)
                flash("Classification modifiée.", "success")
                redirectTo = url_for("classifications.getClassifications")
            except USER_INPUT_ERRORS as error:
                flash(str(error), "error")
                values = request.form
        return (
            redirect(redirectTo)
            if redirectTo
            else render_template(
                "reference/form.html",
                title="Modifier une classification",
                fields=_FIELDS,
                values=values,
                cancelEndpoint="classifications.getClassifications",
                isEdit=True,
            )
        )

    @blueprint.post("/<int:idClassification>/delete")
    def deleteClassification(idClassification: int):
        classificationService.deleteClassification(idClassification)
        flash("Classification supprimée.", "success")
        return redirect(url_for("classifications.getClassifications"))

    return blueprint