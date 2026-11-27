from typing import List

from werkzeug.datastructures import MultiDict

from models import LanguageDTO

from .ApiClient import ApiClient
from .FormParser import FormParser


class LanguageService:
    """Classe qui représente le service de gestion des langues."""

    def __init__(self, apiClient: ApiClient) -> None:
        self._apiClient = apiClient

    def getAllLanguages(self) -> List[LanguageDTO]:
        """
        Méthode qui récupère toutes les langues.

        :return: Liste des langues.
        :raises ClientError: Si l'appel API échoue.
        """
        return [LanguageDTO.fromDict(data) for data in self._apiClient.get("/languages")]

    def searchLanguagesByName(self, name: str) -> List[LanguageDTO]:
        """
        Méthode qui recherche les langues par nom.

        :param name: Nom ou partie du nom recherché.
        :return: Langues correspondantes.
        :raises ClientError: Si l'appel API échoue.
        """
        data = self._apiClient.get("/languages", params={"name": name})
        return [LanguageDTO.fromDict(item) for item in data]

    def getLanguageById(self, idLanguage: int) -> LanguageDTO:
        """
        Méthode qui récupère une langue par identifiant.

        :param idLanguage: Identifiant de la langue.
        :return: Langue correspondante.
        :raises ClientError: Si l'appel API échoue.
        """
        return LanguageDTO.fromDict(self._apiClient.get(f"/languages/{idLanguage}"))

    def getLanguageByCode(self, code: str) -> LanguageDTO:
        """
        Méthode qui récupère une langue par code.

        :param code: Code de la langue.
        :return: Langue correspondante.
        :raises ClientError: Si l'appel API échoue.
        """
        return LanguageDTO.fromDict(self._apiClient.get(f"/languages/code/{code}"))

    def createLanguageFromForm(self, form: MultiDict) -> None:
        """
        Méthode qui crée une langue à partir d'un formulaire.

        :param form: Champs soumis par le formulaire.
        :raises InvalidRequestError: Si un champ obligatoire est invalide.
        :raises ClientError: Si l'appel API échoue.
        """
        language = LanguageDTO(
            idLanguage=0,
            # l'API recherche les codes en minuscules
            code=FormParser.text(form, "code", "Code", required=True).lower(),
            name=FormParser.text(form, "name", "Nom", required=True),
        )
        payload = language.toDict()
        payload.pop("idLanguage", None)
        self._apiClient.post("/languages", payload)

    def updateLanguageFromForm(self, existing: LanguageDTO, form: MultiDict) -> LanguageDTO:
        """
        Méthode qui modifie une langue à partir d'un formulaire.

        :param existing: Langue à modifier.
        :param form: Champs soumis par le formulaire.
        :return: Langue modifiée.
        :raises InvalidRequestError: Si un champ obligatoire est invalide.
        :raises ClientError: Si l'appel API échoue.
        """
        language = LanguageDTO(
            idLanguage=existing.idLanguage,
            code=FormParser.text(form, "code", "Code", required=True).lower(),
            name=FormParser.text(form, "name", "Nom", required=True),
        )
        return LanguageDTO.fromDict(
            self._apiClient.put(
                f"/languages/{existing.idLanguage}", language.toDict()
            )
        )

    def deleteLanguage(self, idLanguage: int) -> None:
        """
        Méthode qui supprime une langue.

        :param idLanguage: Identifiant de la langue.
        :raises ClientError: Si l'appel API échoue.
        """
        self._apiClient.delete(f"/languages/{idLanguage}")