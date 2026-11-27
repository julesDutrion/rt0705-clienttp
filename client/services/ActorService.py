from typing import List

from werkzeug.datastructures import MultiDict

from models import ActorDTO

from .ApiClient import ApiClient
from .FormParser import FormParser


class ActorService:
    """Classe qui représente le service de gestion des acteurs."""

    def __init__(self, apiClient: ApiClient) -> None:
        self._apiClient = apiClient

    def getAllActors(self) -> List[ActorDTO]:
        """
        Méthode qui récupère tous les acteurs.

        :return: Liste des acteurs.
        :raises ClientError: Si l'appel API échoue.
        """
        return [
            ActorDTO.fromDict(data)
            for data in self._apiClient.get("/actors")
        ]

    def searchActorsByName(self, name: str) -> List[ActorDTO]:
        """
        Méthode qui recherche les acteurs par nom.

        :param name: Nom ou partie du nom recherché.
        :return: Acteurs correspondants.
        :raises ClientError: Si l'appel API échoue.
        """
        data = self._apiClient.get("/actors", params={"name": name})
        return [ActorDTO.fromDict(item) for item in data]

    def getActorById(self, idActor: int) -> ActorDTO:
        """
        Méthode qui récupère un acteur par identifiant.

        :param idActor: Identifiant de l'acteur.
        :return: Acteur correspondant.
        :raises ClientError: Si l'appel API échoue.
        """
        return ActorDTO.fromDict(
            self._apiClient.get(f"/actors/{idActor}")
        )

    def createActorFromForm(self, form: MultiDict) -> None:
        """
        Méthode qui crée un acteur à partir d'un formulaire.

        :param form: Champs soumis par le formulaire.
        :raises InvalidRequestError: Si un champ obligatoire est invalide.
        :raises ClientError: Si l'appel API échoue.
        """
        actor = ActorDTO(
            idActor=0,
            firstName=FormParser.text(form, "firstName", "Prénom", required=True),
            lastName=FormParser.text(form, "lastName", "Nom", required=True),
        )
        payload = actor.toDict()
        payload.pop("idActor", None)
        self._apiClient.post("/actors", payload)

    def updateActorFromForm(
        self, existing: ActorDTO, form: MultiDict
    ) -> ActorDTO:
        """
        Méthode qui modifie un acteur à partir d'un formulaire.

        :param existing: Acteur à modifier.
        :param form: Champs soumis par le formulaire.
        :return: Acteur modifié.
        :raises InvalidRequestError: Si un champ obligatoire est invalide.
        :raises ClientError: Si l'appel API échoue.
        """
        actor = ActorDTO(
            idActor=existing.idActor,
            firstName=FormParser.text(form, "firstName", "Prénom", required=True),
            lastName=FormParser.text(form, "lastName", "Nom", required=True),
        )
        return ActorDTO.fromDict(
            self._apiClient.put(f"/actors/{existing.idActor}", actor.toDict())
        )

    def deleteActor(self, idActor: int) -> None:
        """
        Méthode qui supprime un acteur.

        :param idActor: Identifiant de l'acteur.
        :raises ClientError: Si l'appel API échoue.
        """
        self._apiClient.delete(f"/actors/{idActor}")
