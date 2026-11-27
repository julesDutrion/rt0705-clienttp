from typing import Any, Dict, List
from urllib.parse import quote

from models import SupportDTO

from .ApiClient import ApiClient
from exceptions import InvalidRequestError


class SupportService:
    """Classe qui représente le service de gestion des supports."""

    def __init__(self, apiClient: ApiClient) -> None:
        self._apiClient = apiClient

    def getSupportById(self, idSupport: int) -> SupportDTO:
        """
        Méthode qui récupère un support par identifiant.

        :param idSupport: Identifiant du support.
        :return: Support correspondant.
        :raises ClientError: Si l'appel API échoue.
        """
        return SupportDTO.fromDict(self._apiClient.get(f"/supports/{idSupport}"))

    def getSupportsByFilmId(self, idFilm: str) -> List[SupportDTO]:
        """
        Méthode qui récupère les supports d'un film.

        :param idFilm: Identifiant du film.
        :return: Supports associés au film.
        :raises ClientError: Si l'appel API échoue.
        """
        encodedIdFilm = quote(idFilm, safe="")
        data = self._apiClient.get(f"/supports/film/{encodedIdFilm}")
        return [SupportDTO.fromDict(item) for item in data]

    def createSupport(self, support: SupportDTO) -> SupportDTO:
        """
        Méthode qui crée un support.

        :param support: Données du support à créer.
        :return: Support créé.
        :raises ClientError: Si les données ou l'appel API sont invalides.
        """
        return SupportDTO.fromDict(
            self._apiClient.post("/supports", self._payload(support))
        )

    def updateSupport(self, support: SupportDTO) -> SupportDTO:
        """
        Méthode qui modifie un support.

        :param support: Données du support à modifier.
        :return: Support modifié.
        :raises InvalidRequestError: Si le support n'a pas d'identifiant.
        :raises ClientError: Si l'appel API échoue.
        """
        if support.idSupport is None:
            raise InvalidRequestError("Un support existant doit avoir un identifiant.")
        return SupportDTO.fromDict(
            self._apiClient.put(
                f"/supports/{support.idSupport}", self._payload(support)
            )
        )

    def deleteSupport(self, idSupport: int) -> None:
        """
        Méthode qui supprime un support.

        :param idSupport: Identifiant du support.
        :raises ClientError: Si l'appel API échoue.
        """
        self._apiClient.delete(f"/supports/{idSupport}")

    @staticmethod
    def _payload(support: SupportDTO) -> Dict[str, Any]:
        return {
            "idFilm": support.idFilm,
            "idSupportType": support.idSupportType,
            "location": support.location,
            "url": support.url,
        }
