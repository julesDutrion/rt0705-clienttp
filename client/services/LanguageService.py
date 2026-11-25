from typing import List

from werkzeug.datastructures import MultiDict

from models import LanguageDTO

from .ApiClient import ApiClient
from .FormParser import FormParser


class LanguageService:
    def __init__(self, apiClient: ApiClient) -> None:
        self._apiClient = apiClient

    def getAllLanguages(self) -> List[LanguageDTO]:
        return [LanguageDTO.fromDict(data) for data in self._apiClient.get("/languages")]

    def searchLanguagesByName(self, name: str) -> List[LanguageDTO]:
        data = self._apiClient.get("/languages", params={"name": name})
        return [LanguageDTO.fromDict(item) for item in data]

    def getLanguageById(self, idLanguage: int) -> LanguageDTO:
        return LanguageDTO.fromDict(self._apiClient.get(f"/languages/{idLanguage}"))

    def getLanguageByCode(self, code: str) -> LanguageDTO:
        return LanguageDTO.fromDict(self._apiClient.get(f"/languages/code/{code}"))

    def createLanguageFromForm(self, form: MultiDict) -> None:
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
        self._apiClient.delete(f"/languages/{idLanguage}")