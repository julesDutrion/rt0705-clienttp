import unittest
from datetime import date

from werkzeug.datastructures import MultiDict

from exceptions import InvalidRequestError
from models import FilmDTO, SupportDTO, SupportTypeDTO
from services.FilmService import FilmService


class EmptyReferenceService:
    def getAllDirectors(self):
        return []

    def getAllClassifications(self):
        return []

    def getAllLanguages(self):
        return []

    def getAllGenres(self):
        return []

    def getAllActors(self):
        return []


class SupportTypeServiceStub:
    def getAllSupportTypes(self):
        return [
            SupportTypeDTO(idSupportType=1, name="DVD", mode="physical"),
            SupportTypeDTO(idSupportType=2, name="Streaming", mode="digital"),
        ]


class SupportServiceStub:
    def __init__(self):
        self.calls = []

    def createSupport(self, support):
        self.calls.append(("create", support))

    def updateSupport(self, support):
        self.calls.append(("update", support))

    def deleteSupport(self, idSupport):
        self.calls.append(("delete", idSupport))


class ApiClientStub:
    def __init__(self):
        self.lastFilm = None
        self.putBodies = []
        self.postBodies = []

    def post(self, path, body):
        self.postBodies.append((path, body))
        self.lastFilm = {**body, "idFilm": "film-1", "supports": []}
        return self.lastFilm

    def put(self, path, body):
        self.putBodies.append((path, body))
        self.lastFilm = {**body, "supports": []}
        return self.lastFilm

    def get(self, path, params=None):
        return self.lastFilm


def filmForm(*supportFields):
    return MultiDict(
        [
            ("title", "Film modifié"),
            ("synopsis", ""),
            ("releaseDate", "2024-01-02"),
            ("duration", "90"),
            ("posterUrl", ""),
            *supportFields,
        ]
    )


def makeFilm(supports):
    return FilmDTO(
        idFilm="film-1",
        title="Film",
        synopsis="",
        releaseDate=date(2020, 1, 1),
        duration=90,
        posterUrl="",
        addedDate=date(2024, 1, 1),
        supports=supports,
    )


class FilmSupportTests(unittest.TestCase):
    def setUp(self):
        self.api = ApiClientStub()
        self.supportService = SupportServiceStub()
        references = EmptyReferenceService()
        self.filmService = FilmService(
            self.api,
            references,
            references,
            references,
            references,
            references,
            self.supportService,
            SupportTypeServiceStub(),
        )

    def test_general_film_update_without_support_fields_preserves_supports(self):
        existingSupport = SupportDTO(
            idFilm="film-1",
            idSupportType=1,
            idSupport=7,
            location="Étagère A",
        )

        self.filmService.updateFilmFromForm(
            makeFilm([existingSupport]), filmForm()
        )

        self.assertEqual(self.supportService.calls, [])
        self.assertNotIn("supports", self.api.putBodies[0][1])

    def test_support_update_keeps_existing_id_and_adds_and_removes_rows(self):
        existingSupports = [
            SupportDTO(
                idFilm="film-1",
                idSupportType=1,
                idSupport=7,
                location="Étagère A",
            ),
            SupportDTO(
                idFilm="film-1",
                idSupportType=2,
                idSupport=8,
                url="https://example.test/old",
            ),
        ]
        form = filmForm(
            ("supportsSubmitted", "1"),
            ("supportIds", "7"),
            ("supportTypeIds", "1"),
            ("supportLocations", "Étagère A"),
            ("supportUrls", ""),
            ("supportIds", ""),
            ("supportTypeIds", "2"),
            ("supportLocations", ""),
            ("supportUrls", "https://example.test/new"),
        )

        self.filmService.updateFilmFromForm(makeFilm(existingSupports), form)

        calls = self.supportService.calls
        self.assertEqual([call[0] for call in calls], ["create", "delete"])
        self.assertEqual(calls[0][1].idFilm, "film-1")
        self.assertIsNone(calls[0][1].idSupport)
        self.assertEqual(calls[0][1].url, "https://example.test/new")
        self.assertEqual(calls[1], ("delete", 8))

    def test_existing_support_is_updated_with_its_identifier(self):
        existingSupport = SupportDTO(
            idFilm="film-1",
            idSupportType=1,
            idSupport=7,
            location="Étagère A",
        )
        form = filmForm(
            ("supportsSubmitted", "1"),
            ("supportIds", "7"),
            ("supportTypeIds", "1"),
            ("supportLocations", "Étagère B"),
            ("supportUrls", ""),
        )

        self.filmService.updateFilmFromForm(makeFilm([existingSupport]), form)

        self.assertEqual(len(self.supportService.calls), 1)
        operation, support = self.supportService.calls[0]
        self.assertEqual(operation, "update")
        self.assertEqual(support.idSupport, 7)
        self.assertEqual(support.location, "Étagère B")

    def test_create_film_posts_each_support_separately(self):
        form = filmForm(
            ("supportsSubmitted", "1"),
            ("supportIds", ""),
            ("supportTypeIds", "1"),
            ("supportLocations", "Étagère A"),
            ("supportUrls", ""),
            ("supportIds", ""),
            ("supportTypeIds", "2"),
            ("supportLocations", ""),
            ("supportUrls", "https://example.test/video"),
        )

        self.filmService.createFilmFromForm(form)

        self.assertEqual(self.api.postBodies[0][0], "/films")
        self.assertNotIn("supports", self.api.postBodies[0][1])
        self.assertEqual(
            [call[1].idSupportType for call in self.supportService.calls],
            [1, 2],
        )
        self.assertTrue(
            all(call[1].idFilm == "film-1" for call in self.supportService.calls)
        )

    def test_invalid_streaming_url_is_rejected_before_film_creation(self):
        form = filmForm(
            ("supportsSubmitted", "1"),
            ("supportIds", ""),
            ("supportTypeIds", "2"),
            ("supportLocations", ""),
            ("supportUrls", "ftp://example.test/video"),
        )

        with self.assertRaises(InvalidRequestError):
            self.filmService.createFilmFromForm(form)

        self.assertEqual(self.api.postBodies, [])


if __name__ == "__main__":
    unittest.main()
