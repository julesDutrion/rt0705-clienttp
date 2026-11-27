from flask import Blueprint, flash, jsonify, redirect, render_template, request, url_for

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
    """
    Méthode qui crée les routes des réalisateurs.

    :param directorService: Service de gestion des réalisateurs.
    :return: Blueprint Flask des réalisateurs.
    """
    blueprint = Blueprint("directors", __name__, url_prefix="/directors")

    @blueprint.get("/search")
    def searchDirectors():
        """
        Méthode qui recherche les réalisateurs pour le sélecteur de formulaire.

        :return: Réponse JSON des réalisateurs correspondants.
        :raises ClientError: Si l'appel API échoue.
        """
        query = (request.args.get("q") or "").strip()
        if not query:
            return jsonify([])
        return jsonify([
            {
                "id": director.idDirector,
                "label": f"{director.firstName} {director.lastName}",
            }
            for director in directorService.searchDirectorsByName(query)
        ])

    @blueprint.get("")
    def getDirectors():
        """
        Méthode qui affiche la liste des réalisateurs.

        :return: Page HTML des réalisateurs.
        :raises ClientError: Si l'appel API échoue.
        """
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
        """
        Méthode qui affiche ou traite la création d'un réalisateur.

        :return: Formulaire HTML ou redirection après création.
        :raises ClientError: Si un appel API échoue.
        """
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
        """
        Méthode qui affiche ou traite la modification d'un réalisateur.

        :param idDirector: Identifiant du réalisateur.
        :return: Formulaire HTML ou redirection après modification.
        :raises ClientError: Si un appel API échoue.
        """
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
        """
        Méthode qui supprime un réalisateur.

        :param idDirector: Identifiant du réalisateur.
        :return: Redirection vers la liste des réalisateurs.
        :raises ClientError: Si l'appel API échoue.
        """
        directorService.deleteDirector(idDirector)
        flash("Réalisateur supprimé.", "success")
        return redirect(url_for("directors.getDirectors"))

    return blueprint