from datetime import date

import pytest
from werkzeug.datastructures import MultiDict

from exceptions import InvalidRequestError
from services.FormParser import FormParser


def test_text_is_trimmed_and_required_values_are_validated():
    form = MultiDict([("title", "  Film  ")])

    assert FormParser.text(form, "title", "Titre", required=True) == "Film"

    with pytest.raises(InvalidRequestError, match="obligatoire"):
        FormParser.text(MultiDict([("title", "  ")]), "title", "Titre", True)


def test_integer_fields_accept_optional_values_and_reject_invalid_values():
    assert FormParser.optionalInteger(MultiDict(), "age", "Âge") is None
    assert FormParser.requiredInteger(
        MultiDict([("age", "18")]), "age", "Âge"
    ) == 18

    with pytest.raises(InvalidRequestError, match="nombre entier"):
        FormParser.optionalInteger(
            MultiDict([("age", "18.5")]), "age", "Âge"
        )


def test_dates_and_integer_lists_are_parsed_and_deduplicated():
    assert FormParser.requiredDate(
        MultiDict([("date", "2026-11-27")]), "date", "Date"
    ) == date(2026, 11, 27)
    assert FormParser.integerList(
        MultiDict([("ids", "1"), ("ids", "2"), ("ids", "1")]),
        "ids",
        "Identifiants",
    ) == [1, 2]

    with pytest.raises(InvalidRequestError, match="date valide"):
        FormParser.requiredDate(
            MultiDict([("date", "27/11/2026")]), "date", "Date"
        )
