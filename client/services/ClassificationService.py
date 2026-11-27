from typing import List

from werkzeug.datastructures import MultiDict

from exceptions import InvalidRequestError
from models import ClassificationDTO

from .ApiClient import ApiClient
from .FormParser import FormParser


class ClassificationService:
    """Classe qui représente le service de gestion des classifications."""

    def __init__(self, apiClient: ApiClient) -> None:
        self._apiClient = apiClient

    def getAllClassifications(self) -> List[ClassificationDTO]:
        """
        Méthode qui récupère toutes les classifications.

        :return: Liste des classifications.
        :raises ClientError: Si l'appel API échoue.
        """
        data = self._apiClient.get("/classifications")
        return [ClassificationDTO.fromDict(item) for item in data]

    def getClassificationsByMinAge(self, minAge: int) -> List[ClassificationDTO]:
        """
        Méthode qui récupère les classifications à partir d'un âge minimum.

        :param minAge: Âge minimum recherché.
        :return: Classifications correspondantes.
        :raises ClientError: Si l'appel API échoue.
        """
        data = self._apiClient.get("/classifications", params={"minAge": minAge})
        return [ClassificationDTO.fromDict(item) for item in data]

    def getClassificationById(self, idClassification: int) -> ClassificationDTO:
        """
        Méthode qui récupère une classification par identifiant.

        :param idClassification: Identifiant de la classification.
        :return: Classification correspondante.
        :raises ClientError: Si l'appel API échoue.
        """
        return ClassificationDTO.fromDict(
            self._apiClient.get(f"/classifications/{idClassification}")
        )

    def createClassificationFromForm(self, form: MultiDict) -> None:
        """
        Méthode qui crée une classification à partir d'un formulaire.

        :param form: Champs soumis par le formulaire.
        :raises InvalidRequestError: Si l'âge minimum est absent, invalide ou négatif.
        :raises ClientError: Si l'appel API échoue.
        """
        minAge = FormParser.requiredInteger(form, "minAge", "Âge minimum")
        if minAge < 0:
            raise InvalidRequestError("L'âge minimum ne peut pas être négatif.")
        classification = ClassificationDTO(
            idClassification=0,
            minAge=minAge,
        )
        payload = classification.toDict()
        payload.pop("idClassification", None)
        self._apiClient.post("/classifications", payload)

    def updateClassificationFromForm(
        self, existing: ClassificationDTO, form: MultiDict
    ) -> ClassificationDTO:
        """
        Méthode qui modifie une classification à partir d'un formulaire.

        :param existing: Classification à modifier.
        :param form: Champs soumis par le formulaire.
        :return: Classification modifiée.
        :raises InvalidRequestError: Si l'âge minimum est absent, invalide ou négatif.
        :raises ClientError: Si l'appel API échoue.
        """
        minAge = FormParser.requiredInteger(form, "minAge", "Âge minimum")
        if minAge < 0:
            raise InvalidRequestError("L'âge minimum ne peut pas être négatif.")
        classification = ClassificationDTO(
            idClassification=existing.idClassification,
            minAge=minAge,
        )
        return ClassificationDTO.fromDict(
            self._apiClient.put(
                f"/classifications/{existing.idClassification}",
                classification.toDict(),
            )
        )

    def deleteClassification(self, idClassification: int) -> None:
        """
        Méthode qui supprime une classification.

        :param idClassification: Identifiant de la classification.
        :raises ClientError: Si l'appel API échoue.
        """
        self._apiClient.delete(f"/classifications/{idClassification}")