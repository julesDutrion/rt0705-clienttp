from typing import List

from werkzeug.datastructures import MultiDict

from exceptions import InvalidRequestError
from models import SupportTypeDTO

from .ApiClient import ApiClient
from .FormParser import FormParser


class SupportTypeService:
    """Classe qui représente le service de gestion des types de supports."""

    def __init__(self, apiClient: ApiClient) -> None:
        self._apiClient = apiClient

    def getAllSupportTypes(self) -> List[SupportTypeDTO]:
        """
        Méthode qui récupère tous les types de supports.

        :return: Liste des types de supports.
        :raises ClientError: Si l'appel API échoue.
        """
        data = self._apiClient.get("/support-types")
        return [SupportTypeDTO.fromDict(item) for item in data]

    def getSupportTypeById(self, idSupportType: int) -> SupportTypeDTO:
        """
        Méthode qui récupère un type de support par identifiant.

        :param idSupportType: Identifiant du type de support.
        :return: Type de support correspondant.
        :raises ClientError: Si l'appel API échoue.
        """
        return SupportTypeDTO.fromDict(
            self._apiClient.get(f"/support-types/{idSupportType}")
        )

    def createSupportTypeFromForm(self, form: MultiDict) -> None:
        """
        Méthode qui crée un type de support à partir d'un formulaire.

        :param form: Champs soumis par le formulaire.
        :raises InvalidRequestError: Si le nom ou le mode est invalide.
        :raises ClientError: Si l'appel API échoue.
        """
        supportType = self._supportTypeFromForm(form)
        payload = supportType.toDict()
        payload.pop("idSupportType", None)
        self._apiClient.post("/support-types", payload)

    def updateSupportTypeFromForm(
        self, existing: SupportTypeDTO, form: MultiDict
    ) -> SupportTypeDTO:
        """
        Méthode qui modifie un type de support à partir d'un formulaire.

        :param existing: Type de support à modifier.
        :param form: Champs soumis par le formulaire.
        :return: Type de support modifié.
        :raises InvalidRequestError: Si le nom ou le mode est invalide.
        :raises ClientError: Si l'appel API échoue.
        """
        supportType = self._supportTypeFromForm(form)
        supportType.idSupportType = existing.idSupportType
        return SupportTypeDTO.fromDict(
            self._apiClient.put(
                f"/support-types/{existing.idSupportType}",
                supportType.toDict(),
            )
        )

    def deleteSupportType(self, idSupportType: int) -> None:
        """
        Méthode qui supprime un type de support.

        :param idSupportType: Identifiant du type de support.
        :raises ClientError: Si l'appel API échoue.
        """
        self._apiClient.delete(f"/support-types/{idSupportType}")

    @staticmethod
    def _supportTypeFromForm(form: MultiDict) -> SupportTypeDTO:
        name = FormParser.text(form, "name", "Nom", required=True)
        mode = FormParser.text(form, "mode", "Mode", required=True)
        if mode not in {"physical", "digital"}:
            raise InvalidRequestError(
                "Le mode doit être « physical » ou « digital »."
            )
        return SupportTypeDTO(idSupportType=0, name=name, mode=mode)
