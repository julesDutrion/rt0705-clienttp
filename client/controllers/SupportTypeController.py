from flask import Blueprint, flash, redirect, render_template, request, url_for

from exceptions import AlreadyExistsError, USER_INPUT_ERRORS
from services import SupportTypeService

_COLUMNS = [
    {"label": "Identifiant", "key": "idSupportType"},
    {"label": "Nom", "key": "name"},
    {"label": "Mode", "key": "mode"},
]
_FIELDS = [
    {"name": "idSupportType", "label": "Identifiant", "type": "number"},
    {"name": "name", "label": "Nom"},
    {
        "name": "mode",
        "label": "Mode",
        "type": "select",
        "options": [
            {"value": "physical", "label": "Physique"},
            {"value": "digital", "label": "Numérique"},
        ],
    },
]


def createSupportTypeBlueprint(
    supportTypeService: SupportTypeService,
) -> Blueprint:
    blueprint = Blueprint(
        "support_types", __name__, url_prefix="/support-types"
    )

    @blueprint.get("")
    def getSupportTypes():
        return render_template(
            "reference/list.html",
            title="Types de supports",
            items=supportTypeService.getAllSupportTypes(),
            columns=_COLUMNS,
            idKey="idSupportType",
            createEndpoint="support_types.newSupportType",
        )

    @blueprint.route("/new", methods=["GET", "POST"])
    def newSupportType():
        values = None
        redirectTo = None
        if request.method == "POST":
            try:
                supportTypeService.createSupportTypeFromForm(request.form)
                flash("Type de support ajouté.", "success")
                redirectTo = url_for("support_types.getSupportTypes")
            except USER_INPUT_ERRORS as error:
                flash(str(error), "error")
                values = request.form
        return (
            redirect(redirectTo)
            if redirectTo
            else render_template(
                "reference/form.html",
                title="Ajouter un type de support",
                fields=_FIELDS,
                values=values,
                cancelEndpoint="support_types.getSupportTypes",
                isEdit=False,
            )
        )

    @blueprint.route("/<int:idSupportType>/edit", methods=["GET", "POST"])
    def editSupportType(idSupportType: int):
        existing = supportTypeService.getSupportTypeById(idSupportType)
        values = existing
        redirectTo = None
        if request.method == "POST":
            try:
                supportTypeService.updateSupportTypeFromForm(existing, request.form)
                flash("Type de support modifié.", "success")
                redirectTo = url_for("support_types.getSupportTypes")
            except USER_INPUT_ERRORS as error:
                flash(str(error), "error")
                values = request.form
        return (
            redirect(redirectTo)
            if redirectTo
            else render_template(
                "reference/form.html",
                title="Modifier un type de support",
                fields=_FIELDS,
                values=values,
                cancelEndpoint="support_types.getSupportTypes",
                isEdit=True,
            )
        )

    @blueprint.post("/<int:idSupportType>/delete")
    def deleteSupportType(idSupportType: int):
        try:
            supportTypeService.deleteSupportType(idSupportType)
            flash("Type de support supprimé.", "success")
        except AlreadyExistsError as error:
            flash(str(error), "error")
        return redirect(url_for("support_types.getSupportTypes"))

    return blueprint
