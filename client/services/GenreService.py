from typing import List

from werkzeug.datastructures import MultiDict

from models import GenreDTO

from .ApiClient import ApiClient
from .FormParser import FormParser


class GenreService:
    def __init__(self, apiClient: ApiClient) -> None:
        self._apiClient = apiClient

    def getAllGenres(self) -> List[GenreDTO]:
        return [GenreDTO.fromDict(data) for data in self._apiClient.get("/genres")]

    def searchGenresByName(self, name: str) -> List[GenreDTO]:
        data = self._apiClient.get("/genres", params={"name": name})
        return [GenreDTO.fromDict(item) for item in data]

    def getGenreById(self, idGenre: int) -> GenreDTO:
        return GenreDTO.fromDict(self._apiClient.get(f"/genres/{idGenre}"))

    def createGenreFromForm(self, form: MultiDict) -> None:
        genre = GenreDTO(
            idGenre=0,
            nameGenre=FormParser.text(form, "nameGenre", "Nom", required=True),
        )
        payload = genre.toDict()
        payload.pop("idGenre", None)
        self._apiClient.post("/genres", payload)

    def updateGenreFromForm(self, existing: GenreDTO, form: MultiDict) -> GenreDTO:
        genre = GenreDTO(
            idGenre=existing.idGenre,
            nameGenre=FormParser.text(form, "nameGenre", "Nom", required=True),
        )
        return GenreDTO.fromDict(
            self._apiClient.put(f"/genres/{existing.idGenre}", genre.toDict())
        )

    def deleteGenre(self, idGenre: int) -> None:
        self._apiClient.delete(f"/genres/{idGenre}")