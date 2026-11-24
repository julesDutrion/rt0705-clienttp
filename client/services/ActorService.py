from typing import List

from werkzeug.datastructures import MultiDict

from models import ActorDTO

from .ApiClient import ApiClient
from .FormParser import FormParser


class ActorService:
    def __init__(self, apiClient: ApiClient) -> None:
        self._apiClient = apiClient

    def getAllActors(self) -> List[ActorDTO]:
        return [
            ActorDTO.fromDict(data)
            for data in self._apiClient.get("/actors")
        ]

    def searchActorsByName(self, name: str) -> List[ActorDTO]:
        data = self._apiClient.get("/actors", params={"name": name})
        return [ActorDTO.fromDict(item) for item in data]

    def getActorById(self, idActor: int) -> ActorDTO:
        return ActorDTO.fromDict(
            self._apiClient.get(f"/actors/{idActor}")
        )

    def createActorFromForm(self, form: MultiDict) -> None:
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
        actor = ActorDTO(
            idActor=existing.idActor,
            firstName=FormParser.text(form, "firstName", "Prénom", required=True),
            lastName=FormParser.text(form, "lastName", "Nom", required=True),
        )
        return ActorDTO.fromDict(
            self._apiClient.put(f"/actors/{existing.idActor}", actor.toDict())
        )

    def deleteActor(self, idActor: int) -> None:
        self._apiClient.delete(f"/actors/{idActor}")
