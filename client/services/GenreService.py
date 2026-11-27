from typing import List

from werkzeug.datastructures import MultiDict

from models import GenreDTO

from .ApiClient import ApiClient
from .FormParser import FormParser


class GenreService:
    """Classe qui représente le service de gestion des genres."""

    def __init__(self, apiClient: ApiClient) -> None:
        self._apiClient = apiClient

    def getAllGenres(self) -> List[GenreDTO]:
        """
        Méthode qui récupère tous les genres.

        :return: Liste des genres.
        :raises ClientError: Si l'appel API échoue.
        """
        return [GenreDTO.fromDict(data) for data in self._apiClient.get("/genres")]

    def searchGenresByName(self, name: str) -> List[GenreDTO]:
        """
        Méthode qui recherche les genres par nom.

        :param name: Nom ou partie du nom recherché.
        :return: Genres correspondants.
        :raises ClientError: Si l'appel API échoue.
        """
        data = self._apiClient.get("/genres", params={"name": name})
        return [GenreDTO.fromDict(item) for item in data]

    def getGenreById(self, idGenre: int) -> GenreDTO:
        """
        Méthode qui récupère un genre par identifiant.

        :param idGenre: Identifiant du genre.
        :return: Genre correspondant.
        :raises ClientError: Si l'appel API échoue.
        """
        return GenreDTO.fromDict(self._apiClient.get(f"/genres/{idGenre}"))

    def createGenreFromForm(self, form: MultiDict) -> None:
        """
        Méthode qui crée un genre à partir d'un formulaire.

        :param form: Champs soumis par le formulaire.
        :raises InvalidRequestError: Si le nom obligatoire est absent.
        :raises ClientError: Si l'appel API échoue.
        """
        genre = GenreDTO(
            idGenre=0,
            nameGenre=FormParser.text(form, "nameGenre", "Nom", required=True),
        )
        payload = genre.toDict()
        payload.pop("idGenre", None)
        self._apiClient.post("/genres", payload)

    def updateGenreFromForm(self, existing: GenreDTO, form: MultiDict) -> GenreDTO:
        """
        Méthode qui modifie un genre à partir d'un formulaire.

        :param existing: Genre à modifier.
        :param form: Champs soumis par le formulaire.
        :return: Genre modifié.
        :raises InvalidRequestError: Si le nom obligatoire est absent.
        :raises ClientError: Si l'appel API échoue.
        """
        genre = GenreDTO(
            idGenre=existing.idGenre,
            nameGenre=FormParser.text(form, "nameGenre", "Nom", required=True),
        )
        return GenreDTO.fromDict(
            self._apiClient.put(f"/genres/{existing.idGenre}", genre.toDict())
        )

    def deleteGenre(self, idGenre: int) -> None:
        """
        Méthode qui supprime un genre.

        :param idGenre: Identifiant du genre.
        :raises ClientError: Si l'appel API échoue.
        """
        self._apiClient.delete(f"/genres/{idGenre}")