from flask import Blueprint, flash, jsonify, redirect, render_template, request, url_for

from exceptions import USER_INPUT_ERRORS
from services import LanguageService

_COLUMNS = [
    {"label": "Identifiant", "key": "idLanguage"},
    {"label": "Code", "key": "code"},
    {"label": "Nom", "key": "name"},
]
_FIELDS = [
    {"name": "idLanguage", "label": "Identifiant", "type": "number"},
    {"name": "code", "label": "Code"},
    {"name": "name", "label": "Nom"},
]


def createLanguageBlueprint(languageService: LanguageService) -> Blueprint:
    blueprint = Blueprint("languages", __name__, url_prefix="/languages")

    @blueprint.get("/search")
    def searchLanguages():
        name = (request.args.get("q") or "").strip()
        if not name:
            return jsonify([])
        return jsonify(
            [
                {
                    "id": language.idLanguage,
                    "label": f"{language.name} ({language.code})",
                }
                for language in languageService.searchLanguagesByName(name)
            ]
        )

    @blueprint.get("")
    def getLanguages():
        return render_template(
            "reference/list.html",
            title="Langues",
            items=languageService.getAllLanguages(),
            columns=_COLUMNS,
            filterParam="language",
            idKey="idLanguage",
            createEndpoint="languages.newLanguage",
        )

    @blueprint.route("/new", methods=["GET", "POST"])
    def newLanguage():
        values = None
        redirectTo = None
        if request.method == "POST":
            try:
                languageService.createLanguageFromForm(request.form)
                flash("Langue ajoutée.", "success")
                redirectTo = url_for("languages.getLanguages")
            except USER_INPUT_ERRORS as error:
                flash(str(error), "error")
                values = request.form
        return (
            redirect(redirectTo)
            if redirectTo
            else render_template(
                "reference/form.html",
                title="Ajouter une langue",
                fields=_FIELDS,
                values=values,
                cancelEndpoint="languages.getLanguages",
                isEdit=False,
            )
        )

    @blueprint.route("/<int:idLanguage>/edit", methods=["GET", "POST"])
    def editLanguage(idLanguage: int):
        existing = languageService.getLanguageById(idLanguage)
        values = existing
        redirectTo = None
        if request.method == "POST":
            try:
                languageService.updateLanguageFromForm(existing, request.form)
                flash("Langue modifiée.", "success")
                redirectTo = url_for("languages.getLanguages")
            except USER_INPUT_ERRORS as error:
                flash(str(error), "error")
                values = request.form
        return (
            redirect(redirectTo)
            if redirectTo
            else render_template(
                "reference/form.html",
                title="Modifier une langue",
                fields=_FIELDS,
                values=values,
                cancelEndpoint="languages.getLanguages",
                isEdit=True,
            )
        )

    @blueprint.post("/<int:idLanguage>/delete")
    def deleteLanguage(idLanguage: int):
        languageService.deleteLanguage(idLanguage)
        flash("Langue supprimée.", "success")
        return redirect(url_for("languages.getLanguages"))

    return blueprint