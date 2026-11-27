from flask import Blueprint, flash, jsonify, redirect, render_template, request, url_for

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
    """
    Méthode qui crée les routes des acteurs.

    :param actorService: Service de gestion des acteurs.
    :return: Blueprint Flask des acteurs.
    """
    blueprint = Blueprint("actors", __name__, url_prefix="/actors")

    @blueprint.get("/search")
    def searchActors():
        """
        Méthode qui recherche les acteurs pour le sélecteur de formulaire.

        :return: Réponse JSON des acteurs correspondants.
        :raises ClientError: Si l'appel API échoue.
        """
        query = (request.args.get("q") or "").strip()
        if not query:
            return jsonify([])
        return jsonify([
            {
                "id": actor.idActor,
                "label": f"{actor.firstName} {actor.lastName}",
            }
            for actor in actorService.searchActorsByName(query)
        ])

    @blueprint.get("")
    def getActors():
        """
        Méthode qui affiche la liste des acteurs.

        :return: Page HTML des acteurs.
        :raises ClientError: Si l'appel API échoue.
        """
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
        """
        Méthode qui affiche ou traite la création d'un acteur.

        :return: Formulaire HTML ou redirection après création.
        :raises ClientError: Si un appel API échoue.
        """
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
        """
        Méthode qui affiche ou traite la modification d'un acteur.

        :param idActor: Identifiant de l'acteur.
        :return: Formulaire HTML ou redirection après modification.
        :raises ClientError: Si un appel API échoue.
        """
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
        """
        Méthode qui supprime un acteur.

        :param idActor: Identifiant de l'acteur.
        :return: Redirection vers la liste des acteurs.
        :raises ClientError: Si l'appel API échoue.
        """
        actorService.deleteActor(idActor)
        flash("Acteur supprimé.", "success")
        return redirect(url_for("actors.getActors"))

    return blueprint
