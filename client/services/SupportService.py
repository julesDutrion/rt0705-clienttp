from typing import Any, Dict, List
from urllib.parse import quote

from models import SupportDTO

from .ApiClient import ApiClient
from exceptions import InvalidRequestError


class SupportService:
    def __init__(self, apiClient: ApiClient) -> None:
        self._apiClient = apiClient

    def getSupportById(self, idSupport: int) -> SupportDTO:
        return SupportDTO.fromDict(self._apiClient.get(f"/supports/{idSupport}"))

    def getSupportsByFilmId(self, idFilm: str) -> List[SupportDTO]:
        encodedIdFilm = quote(idFilm, safe="")
        data = self._apiClient.get(f"/supports/film/{encodedIdFilm}")
        return [SupportDTO.fromDict(item) for item in data]

    def createSupport(self, support: SupportDTO) -> SupportDTO:
        return SupportDTO.fromDict(
            self._apiClient.post("/supports", self._payload(support))
        )

    def updateSupport(self, support: SupportDTO) -> SupportDTO:
        if support.idSupport is None:
            raise InvalidRequestError("Un support existant doit avoir un identifiant.")
        return SupportDTO.fromDict(
            self._apiClient.put(
                f"/supports/{support.idSupport}", self._payload(support)
            )
        )

    def deleteSupport(self, idSupport: int) -> None:
        self._apiClient.delete(f"/supports/{idSupport}")

    @staticmethod
    def _payload(support: SupportDTO) -> Dict[str, Any]:
        return {
            "idFilm": support.idFilm,
            "idSupportType": support.idSupportType,
            "location": support.location,
            "url": support.url,
        }
