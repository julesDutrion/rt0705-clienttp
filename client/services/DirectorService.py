from typing import List

from werkzeug.datastructures import MultiDict

from models import DirectorDTO

from .ApiClient import ApiClient
from .FormParser import FormParser


class DirectorService:
    """Classe qui représente le service de gestion des réalisateurs."""

    def __init__(self, apiClient: ApiClient) -> None:
        self._apiClient = apiClient

    def getAllDirectors(self) -> List[DirectorDTO]:
        """
        Méthode qui récupère tous les réalisateurs.

        :return: Liste des réalisateurs.
        :raises ClientError: Si l'appel API échoue.
        """
        return [DirectorDTO.fromDict(data) for data in self._apiClient.get("/directors")]

    def searchDirectorsByName(self, name: str) -> List[DirectorDTO]:
        """
        Méthode qui recherche les réalisateurs par nom.

        :param name: Nom ou partie du nom recherché.
        :return: Réalisateurs correspondants.
        :raises ClientError: Si l'appel API échoue.
        """
        data = self._apiClient.get("/directors", params={"name": name})
        return [DirectorDTO.fromDict(item) for item in data]

    def getDirectorById(self, idDirector: int) -> DirectorDTO:
        """
        Méthode qui récupère un réalisateur par identifiant.

        :param idDirector: Identifiant du réalisateur.
        :return: Réalisateur correspondant.
        :raises ClientError: Si l'appel API échoue.
        """
        return DirectorDTO.fromDict(self._apiClient.get(f"/directors/{idDirector}"))

    def createDirectorFromForm(self, form: MultiDict) -> None:
        """
        Méthode qui crée un réalisateur à partir d'un formulaire.

        :param form: Champs soumis par le formulaire.
        :raises InvalidRequestError: Si un champ obligatoire est invalide.
        :raises ClientError: Si l'appel API échoue.
        """
        director = DirectorDTO(
            idDirector=0,
            lastName=FormParser.text(form, "lastName", "Nom", required=True),
            firstName=FormParser.text(form, "firstName", "Prénom", required=True),
        )
        payload = director.toDict()
        payload.pop("idDirector", None)
        self._apiClient.post("/directors", payload)

    def updateDirectorFromForm(self, existing: DirectorDTO, form: MultiDict) -> DirectorDTO:
        """
        Méthode qui modifie un réalisateur à partir d'un formulaire.

        :param existing: Réalisateur à modifier.
        :param form: Champs soumis par le formulaire.
        :return: Réalisateur modifié.
        :raises InvalidRequestError: Si un champ obligatoire est invalide.
        :raises ClientError: Si l'appel API échoue.
        """
        director = DirectorDTO(
            idDirector=existing.idDirector,
            lastName=FormParser.text(form, "lastName", "Nom", required=True),
            firstName=FormParser.text(form, "firstName", "Prénom", required=True),
        )
        return DirectorDTO.fromDict(
            self._apiClient.put(
                f"/directors/{existing.idDirector}", director.toDict()
            )
        )

    def deleteDirector(self, idDirector: int) -> None:
        """
        Méthode qui supprime un réalisateur.

        :param idDirector: Identifiant du réalisateur.
        :raises ClientError: Si l'appel API échoue.
        """
        self._apiClient.delete(f"/directors/{idDirector}")