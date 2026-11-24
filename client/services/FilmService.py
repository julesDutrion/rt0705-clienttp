from datetime import date
from typing import Any, Dict, List, Optional
from urllib.parse import quote

from werkzeug.datastructures import MultiDict

from exceptions import InvalidReferenceError, InvalidRequestError
from models import ActorDTO, FilmDTO, SupportDTO

from .ApiClient import ApiClient
from .ClassificationService import ClassificationService
from .DirectorService import DirectorService
from .FormParser import FormParser
from .GenreService import GenreService
from .LanguageService import LanguageService
from .ActorService import ActorService


class FilmService:
    def __init__(
        self,
        apiClient: ApiClient,
        directorService: DirectorService,
        genreService: GenreService,
        languageService: LanguageService,
        classificationService: ClassificationService,
        actorService: ActorService,
    ) -> None:
        self._apiClient = apiClient
        self._directorService = directorService
        self._genreService = genreService
        self._languageService = languageService
        self._classificationService = classificationService
        self._actorService = actorService

    # ------------------------------------------------------------------ #
    # Lecture
    # ------------------------------------------------------------------ #
    def searchFilms(
        self,
        title: Optional[str] = None,
        idGenre: Optional[int] = None,
        idDirector: Optional[int] = None,
        idLanguage: Optional[int] = None,
        idActor: Optional[int] = None,
    ) -> List[FilmDTO]:
        """Sans critère : tout le catalogue. Les critères se cumulent (ET), comme côté API."""
        params: Dict[str, Any] = {}
        if title:
            params["title"] = title
        if idGenre is not None:
            params["genre"] = idGenre
        if idDirector is not None:
            params["director"] = idDirector
        if idLanguage is not None:
            params["language"] = idLanguage
        if idActor is not None:
            params["actor"] = idActor
        data = self._apiClient.get("/films", params=params or None)
        return [FilmDTO.fromDict(item) for item in data]

    def getFilmById(self, idFilm: str) -> FilmDTO:
        return FilmDTO.fromDict(self._apiClient.get(f"/films/{quote(idFilm, safe='')}"))

    # ------------------------------------------------------------------ #
    # Écriture
    # ------------------------------------------------------------------ #
    def createFilmFromForm(self, form: MultiDict) -> Optional[FilmDTO]:
        film = self._buildFilm(
            form, idFilm=None, addedDate=date.today(), support=None
        )
        payload = film.toDict()
        payload.pop("idFilm", None)
        createdFilm = self._apiClient.post("/films", payload)
        return FilmDTO.fromDict(createdFilm) if createdFilm else None

    def updateFilmFromForm(self, existingFilm: FilmDTO, form: MultiDict) -> FilmDTO:
        """Conserve le support et la date d'ajout tout en modifiant les acteurs
        sélectionnés et les autres associations du formulaire."""
        film = self._buildFilm(
            form,
            idFilm=existingFilm.idFilm,
            addedDate=existingFilm.addedDate,
            support=existingFilm.support,
        )
        path = f"/films/{quote(film.idFilm, safe='')}"
        return FilmDTO.fromDict(self._apiClient.put(path, film.toDict()))

    def deleteFilm(self, idFilm: str) -> None:
        self._apiClient.delete(f"/films/{quote(idFilm, safe='')}")

    # ------------------------------------------------------------------ #
    # Interne : formulaire (identifiants) -> FilmDTO (objets complets, comme l'API les attend)
    # ------------------------------------------------------------------ #
    def _buildFilm(
        self,
        form: MultiDict,
        idFilm: Optional[str],
        addedDate: date,
        support: Optional[SupportDTO],
    ) -> FilmDTO:
        duration = FormParser.requiredInteger(form, "duration", "Durée")
        if duration <= 0:
            raise InvalidRequestError("La durée doit être supérieure à 0.")

        directors = {d.idDirector: d for d in self._directorService.getAllDirectors()}
        classifications = {
            c.idClassification: c for c in self._classificationService.getAllClassifications()
        }
        languages = {l.idLanguage: l for l in self._languageService.getAllLanguages()}
        genres = {g.idGenre: g for g in self._genreService.getAllGenres()}
        actors = {a.idActor: a for a in self._actorService.getAllActors()}

        return FilmDTO(
            idFilm=idFilm or "",
            title=FormParser.text(form, "title", "Titre", required=True),
            synopsis=FormParser.text(form, "synopsis", "Synopsis"),
            releaseDate=FormParser.requiredDate(form, "releaseDate", "Date de sortie"),
            duration=duration,
            posterUrl=FormParser.text(form, "posterUrl", "URL de l'affiche"),
            addedDate=addedDate,
            director=self._pickOne(
                directors, FormParser.optionalInteger(form, "idDirector", "Réalisateur"), "Réalisateur"
            ),
            classification=self._pickOne(
                classifications,
                FormParser.optionalInteger(form, "idClassification", "Classification"),
                "Classification",
            ),
            support=support,
            nativeLanguage=self._pickOne(
                languages,
                FormParser.optionalInteger(form, "idNativeLanguage", "Langue d'origine"),
                "Langue",
            ),
            languages=self._pickMany(
                languages, FormParser.integerList(form, "idLanguages", "Langues disponibles"), "Langue"
            ),
            genre=self._pickMany(
                genres, FormParser.integerList(form, "idGenres", "Genres"), "Genre"
            ),
            actors=self._pickMany(
                actors,
                FormParser.integerList(form, "idActors", "Acteurs"),
                "Acteur",
            ),
        )

    @staticmethod
    def _pickOne(catalog: Dict[int, Any], identifier: Optional[int], label: str) -> Optional[Any]:
        if identifier is None:
            return None
        if identifier not in catalog:
            raise InvalidReferenceError(f"{label} {identifier} : élément inexistant.")
        return catalog[identifier]

    @staticmethod
    def _pickMany(catalog: Dict[int, Any], identifiers: List[int], label: str) -> List[Any]:
        return [FilmService._pickOne(catalog, identifier, label) for identifier in identifiers]