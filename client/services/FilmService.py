from datetime import date
from typing import Any, Dict, List, Optional
from urllib.parse import quote, urlparse

from werkzeug.datastructures import MultiDict

from exceptions import (
    USER_INPUT_ERRORS,
    ApiError,
    InvalidReferenceError,
    InvalidRequestError,
    NotFoundError,
)
from models import ActorDTO, DirectorDTO, FilmDTO, LanguageDTO, SupportDTO

from .ApiClient import ApiClient
from .ClassificationService import ClassificationService
from .FormParser import FormParser
from .GenreService import GenreService
from .ActorService import ActorService
from .SupportService import SupportService
from .SupportTypeService import SupportTypeService


class FilmService:
    """Classe qui représente le service de gestion des films."""

    def __init__(
        self,
        apiClient: ApiClient,
        genreService: GenreService,
        classificationService: ClassificationService,
        actorService: ActorService,
        supportService: SupportService,
        supportTypeService: SupportTypeService,
    ) -> None:
        self._apiClient = apiClient
        self._genreService = genreService
        self._classificationService = classificationService
        self._actorService = actorService
        self._supportService = supportService
        self._supportTypeService = supportTypeService

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
        idSupportType: Optional[int] = None,
    ) -> List[FilmDTO]:
        """
        Méthode qui recherche les films selon les critères fournis.

        :param title: Titre ou partie du titre recherché.
        :param idGenre: Identifiant du genre recherché.
        :param idDirector: Identifiant du réalisateur recherché.
        :param idLanguage: Identifiant de la langue recherchée.
        :param idActor: Identifiant de l'acteur recherché.
        :param idSupportType: Identifiant du type de support recherché.
        :return: Films correspondant aux critères.
        :raises ClientError: Si l'appel API échoue.
        """
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
        if idSupportType is not None:
            params["supportType"] = idSupportType
        data = self._apiClient.get("/films", params=params or None)
        return [FilmDTO.fromDict(item) for item in data]

    def getFilmById(self, idFilm: str) -> FilmDTO:
        """
        Méthode qui récupère un film et ses supports par identifiant.

        :param idFilm: Identifiant du film.
        :return: Film correspondant avec ses supports.
        :raises ClientError: Si le film ou un support est introuvable.
        """
        film = FilmDTO.fromDict(
            self._apiClient.get(f"/films/{quote(idFilm, safe='')}")
        )
        film.supports = self._supportService.getSupportsByFilmId(film.idFilm)
        return film

    def getFilmTitleById(self, idFilm: str) -> str:
        """
        Méthode qui récupère le titre d'un film.

        :param idFilm: Identifiant du film.
        :return: Titre du film.
        :raises ClientError: Si l'appel API échoue.
        """
        data = self._apiClient.get(f"/films/{quote(idFilm, safe='')}")
        return FilmDTO.fromDict(data).title

    # ------------------------------------------------------------------ #
    # Écriture
    # ------------------------------------------------------------------ #
    def createFilmFromForm(self, form: MultiDict) -> Optional[FilmDTO]:
        """
        Méthode qui crée un film à partir d'un formulaire.

        :param form: Champs soumis par le formulaire.
        :return: Film créé, ou `None` si l'API ne le retourne pas.
        :raises ClientError: Si les données ou un appel API sont invalides.
        """
        supports = (
            self._buildSupports(form, "", [])
            if form.get("supportsSubmitted") == "1"
            else []
        )
        film = self._buildFilm(form, idFilm=None, addedDate=date.today())
        createdFilm = self._apiClient.post("/films", self._filmPayload(film, includeId=False))
        if not createdFilm:
            raise ApiError("L'API n'a pas renvoyé le film créé.")

        created = FilmDTO.fromDict(createdFilm)
        if supports:
            try:
                for support in supports:
                    support.idFilm = created.idFilm
                    self._supportService.createSupport(support)
            except USER_INPUT_ERRORS as error:
                raise ApiError(
                    "Le film a été créé, mais ses supports n'ont pas tous été enregistrés."
                ) from error
            return self.getFilmById(created.idFilm)
        return created

    def updateFilmFromForm(self, existingFilm: FilmDTO, form: MultiDict) -> FilmDTO:
        """
        Méthode qui modifie un film et ses supports soumis.

        :param existingFilm: Film à modifier.
        :param form: Champs soumis par le formulaire.
        :return: Film modifié.
        :raises ClientError: Si les données ou un appel API sont invalides.
        """
        supportsSubmitted = form.get("supportsSubmitted") == "1"
        supports = (
            self._buildSupports(form, existingFilm.idFilm, existingFilm.supports)
            if supportsSubmitted
            else []
        )
        film = self._buildFilm(
            form,
            idFilm=existingFilm.idFilm,
            addedDate=existingFilm.addedDate,
        )
        path = f"/films/{quote(film.idFilm, safe='')}"
        updated = FilmDTO.fromDict(
            self._apiClient.put(path, self._filmPayload(film, includeId=True))
        )
        if supportsSubmitted:
            try:
                self._syncSupports(existingFilm.supports, supports)
            except USER_INPUT_ERRORS as error:
                raise ApiError(
                    "Le film a été modifié, mais ses supports n'ont pas tous été synchronisés."
                ) from error
            return self.getFilmById(film.idFilm)
        return updated

    def deleteFilm(self, idFilm: str) -> None:
        """
        Méthode qui supprime un film.

        :param idFilm: Identifiant du film.
        :raises ClientError: Si l'appel API échoue.
        """
        self._apiClient.delete(f"/films/{quote(idFilm, safe='')}")

    # ------------------------------------------------------------------ #
    # Interne : formulaire (identifiants) -> FilmDTO (objets complets, comme l'API les attend)
    # ------------------------------------------------------------------ #
    def _buildFilm(
        self,
        form: MultiDict,
        idFilm: Optional[str],
        addedDate: date,
    ) -> FilmDTO:
        duration = FormParser.requiredInteger(form, "duration", "Durée")
        if duration <= 0:
            raise InvalidRequestError("La durée doit être supérieure à 0.")

        classifications = {
            c.idClassification: c for c in self._classificationService.getAllClassifications()
        }
        genres = {g.idGenre: g for g in self._genreService.getAllGenres()}
        directorId = FormParser.optionalInteger(form, "idDirector", "Réalisateur")
        nativeLanguageId = FormParser.optionalInteger(
            form, "idNativeLanguage", "Langue d'origine"
        )
        languageIds = FormParser.integerList(
            form, "idLanguages", "Langues disponibles"
        )
        actorIds = FormParser.integerList(form, "idActors", "Acteurs")

        for idActor in actorIds:
            try:
                self._actorService.getActorById(idActor)
            except NotFoundError as error:
                raise InvalidReferenceError(
                    f"Acteur {idActor} : élément inexistant."
                ) from error

        return FilmDTO(
            idFilm=idFilm or "",
            title=FormParser.text(form, "title", "Titre", required=True),
            synopsis=FormParser.text(form, "synopsis", "Synopsis"),
            releaseDate=FormParser.requiredDate(form, "releaseDate", "Date de sortie"),
            duration=duration,
            posterUrl=FormParser.text(form, "posterUrl", "URL de l'affiche"),
            addedDate=addedDate,
            director=(
                DirectorDTO(
                    idDirector=directorId,
                    lastName="",
                    firstName="",
                )
                if directorId is not None
                else None
            ),
            classification=self._pickOne(
                classifications,
                FormParser.optionalInteger(form, "idClassification", "Classification"),
                "Classification",
            ),
            nativeLanguage=(
                LanguageDTO(idLanguage=nativeLanguageId, code="", name="")
                if nativeLanguageId is not None
                else None
            ),
            languages=[
                LanguageDTO(idLanguage=idLanguage, code="", name="")
                for idLanguage in languageIds
            ],
            genre=self._pickMany(
                genres, FormParser.integerList(form, "idGenres", "Genres"), "Genre"
            ),
            actors=[
                ActorDTO(idActor=idActor, firstName="", lastName="")
                for idActor in actorIds
            ],
        )

    def _buildSupports(
        self,
        form: MultiDict,
        idFilm: str,
        existingSupports: List[SupportDTO],
    ) -> List[SupportDTO]:
        supportIds = form.getlist("supportIds")
        supportTypeIds = form.getlist("supportTypeIds")
        locations = form.getlist("supportLocations")
        urls = form.getlist("supportUrls")
        rowCount = len(supportTypeIds)
        if any(len(values) != rowCount for values in (supportIds, locations, urls)):
            raise InvalidRequestError("Les informations des supports sont incomplètes.")

        supportTypes = {
            supportType.idSupportType: supportType
            for supportType in self._supportTypeService.getAllSupportTypes()
        }
        existingById = {
            support.idSupport: support
            for support in existingSupports
            if support.idSupport is not None
        }
        parsedSupports: List[SupportDTO] = []
        seenIds = set()

        for rawId, rawTypeId, rawLocation, rawUrl in zip(
            supportIds, supportTypeIds, locations, urls
        ):
            try:
                idSupport = int(rawId) if rawId.strip() else None
                idSupportType = int(rawTypeId)
            except ValueError:
                raise InvalidRequestError("Un identifiant de support est invalide.")

            supportType = supportTypes.get(idSupportType)
            if supportType is None:
                raise InvalidReferenceError(
                    f"Type de support {idSupportType} : élément inexistant."
                )
            if idSupport is not None:
                if idSupport not in existingById or idSupport in seenIds:
                    raise InvalidReferenceError(
                        f"Le support {idSupport} n'est pas associé à ce film."
                    )
                seenIds.add(idSupport)

            location = rawLocation.strip()
            url = rawUrl.strip()
            if supportType.mode == "physical":
                if not location:
                    raise InvalidRequestError(
                        "La localisation est obligatoire pour un support physique."
                    )
                parsedSupports.append(
                    SupportDTO(
                        idFilm=idFilm,
                        idSupportType=idSupportType,
                        idSupport=idSupport,
                        location=location,
                    )
                )
            elif supportType.mode == "digital":
                try:
                    parsedUrl = urlparse(url)
                    isValidUrl = (
                        parsedUrl.scheme in {"http", "https"}
                        and bool(parsedUrl.hostname)
                    )
                except ValueError:
                    isValidUrl = False
                if not isValidUrl:
                    raise InvalidRequestError(
                        "L'URL doit être une adresse HTTP ou HTTPS valide."
                    )
                parsedSupports.append(
                    SupportDTO(
                        idFilm=idFilm,
                        idSupportType=idSupportType,
                        idSupport=idSupport,
                        url=url,
                    )
                )
            else:
                raise InvalidRequestError(
                    f"Mode de support non pris en charge : {supportType.mode}."
                )
        return parsedSupports

    def _syncSupports(
        self,
        existingSupports: List[SupportDTO],
        submittedSupports: List[SupportDTO],
    ) -> None:
        existingById = {
            support.idSupport: support
            for support in existingSupports
            if support.idSupport is not None
        }
        retainedIds = {
            support.idSupport
            for support in submittedSupports
            if support.idSupport is not None
        }
        for support in submittedSupports:
            if support.idSupport is None:
                self._supportService.createSupport(support)
            elif self._supportChanged(existingById[support.idSupport], support):
                self._supportService.updateSupport(support)
        for support in existingSupports:
            if support.idSupport is not None and support.idSupport not in retainedIds:
                self._supportService.deleteSupport(support.idSupport)

    @staticmethod
    def _supportChanged(existing: SupportDTO, submitted: SupportDTO) -> bool:
        return (
            existing.idSupportType != submitted.idSupportType
            or existing.location != submitted.location
            or existing.url != submitted.url
        )

    @staticmethod
    def _filmPayload(film: FilmDTO, includeId: bool) -> Dict[str, Any]:
        payload = film.toDict()
        payload.pop("supports", None)
        payload["director"] = (
            {"idDirector": film.director.idDirector} if film.director else None
        )
        payload["nativeLanguage"] = (
            {"idLanguage": film.nativeLanguage.idLanguage}
            if film.nativeLanguage
            else None
        )
        payload["languages"] = [
            {"idLanguage": language.idLanguage} for language in film.languages
        ]
        payload["actors"] = [
            {"idActor": actor.idActor} for actor in film.actors
        ]
        if not includeId:
            payload.pop("idFilm", None)
        return payload

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