from typing import List

from werkzeug.datastructures import MultiDict

from models import DirectorDTO

from .ApiClient import ApiClient
from .FormParser import FormParser


class DirectorService:
    def __init__(self, apiClient: ApiClient) -> None:
        self._apiClient = apiClient

    def getAllDirectors(self) -> List[DirectorDTO]:
        return [DirectorDTO.fromDict(data) for data in self._apiClient.get("/directors")]

    def searchDirectorsByName(self, name: str) -> List[DirectorDTO]:
        data = self._apiClient.get("/directors", params={"name": name})
        return [DirectorDTO.fromDict(item) for item in data]

    def getDirectorById(self, idDirector: int) -> DirectorDTO:
        return DirectorDTO.fromDict(self._apiClient.get(f"/directors/{idDirector}"))

    def createDirectorFromForm(self, form: MultiDict) -> None:
        director = DirectorDTO(
            idDirector=0,
            lastName=FormParser.text(form, "lastName", "Nom", required=True),
            firstName=FormParser.text(form, "firstName", "Prénom", required=True),
        )
        payload = director.toDict()
        payload.pop("idDirector", None)
        self._apiClient.post("/directors", payload)

    def updateDirectorFromForm(self, existing: DirectorDTO, form: MultiDict) -> DirectorDTO:
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
        self._apiClient.delete(f"/directors/{idDirector}")