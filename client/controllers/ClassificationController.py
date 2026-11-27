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
    """
    Méthode qui crée les routes des classifications.

    :param classificationService: Service de gestion des classifications.
    :return: Blueprint Flask des classifications.
    """
    blueprint = Blueprint("classifications", __name__, url_prefix="/classifications")

    @blueprint.get("")
    def getClassifications():
        """
        Méthode qui affiche la liste des classifications.

        :return: Page HTML des classifications.
        :raises ClientError: Si l'appel API échoue.
        """
        # L'API ne permet pas de filtrer les films par classification : pas de lien « Voir les films ».
        return render_template(
            "reference/list.html",
            title="Classifications",
            items=classificationService.getAllClassifications(),
            columns=_COLUMNS,
            idKey="idClassification",
            createEndpoint="classifications.newClassification",
        )

    @blueprint.route("/new", methods=["GET", "POST"])
    def newClassification():
        """
        Méthode qui affiche ou traite la création d'une classification.

        :return: Formulaire HTML ou redirection après création.
        :raises ClientError: Si un appel API échoue.
        """
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
        """
        Méthode qui affiche ou traite la modification d'une classification.

        :param idClassification: Identifiant de la classification.
        :return: Formulaire HTML ou redirection après modification.
        :raises ClientError: Si un appel API échoue.
        """
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
        """
        Méthode qui supprime une classification.

        :param idClassification: Identifiant de la classification.
        :return: Redirection vers la liste des classifications.
        :raises ClientError: Si l'appel API échoue.
        """
        classificationService.deleteClassification(idClassification)
        flash("Classification supprimée.", "success")
        return redirect(url_for("classifications.getClassifications"))

    return blueprint