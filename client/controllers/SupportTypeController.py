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
    """
    Méthode qui crée les routes des types de supports.

    :param supportTypeService: Service de gestion des types de supports.
    :return: Blueprint Flask des types de supports.
    """
    blueprint = Blueprint(
        "support_types", __name__, url_prefix="/support-types"
    )

    @blueprint.get("")
    def getSupportTypes():
        """
        Méthode qui affiche la liste des types de supports.

        :return: Page HTML des types de supports.
        :raises ClientError: Si l'appel API échoue.
        """
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
        """
        Méthode qui affiche ou traite la création d'un type de support.

        :return: Formulaire HTML ou redirection après création.
        :raises ClientError: Si un appel API échoue.
        """
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
        """
        Méthode qui affiche ou traite la modification d'un type de support.

        :param idSupportType: Identifiant du type de support.
        :return: Formulaire HTML ou redirection après modification.
        :raises ClientError: Si un appel API échoue.
        """
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
        """
        Méthode qui supprime un type de support.

        :param idSupportType: Identifiant du type de support.
        :return: Redirection vers la liste des types.
        :raises ClientError: Si l'appel API échoue hors conflit pris en charge.
        """
        try:
            supportTypeService.deleteSupportType(idSupportType)
            flash("Type de support supprimé.", "success")
        except AlreadyExistsError as error:
            flash(str(error), "error")
        return redirect(url_for("support_types.getSupportTypes"))

    return blueprint
