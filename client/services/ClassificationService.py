from typing import List

from werkzeug.datastructures import MultiDict

from exceptions import InvalidRequestError
from models import ClassificationDTO

from .ApiClient import ApiClient
from .FormParser import FormParser


class ClassificationService:
    def __init__(self, apiClient: ApiClient) -> None:
        self._apiClient = apiClient

    def getAllClassifications(self) -> List[ClassificationDTO]:
        data = self._apiClient.get("/classifications")
        return [ClassificationDTO.fromDict(item) for item in data]

    def getClassificationsByMinAge(self, minAge: int) -> List[ClassificationDTO]:
        data = self._apiClient.get("/classifications", params={"minAge": minAge})
        return [ClassificationDTO.fromDict(item) for item in data]

    def getClassificationById(self, idClassification: int) -> ClassificationDTO:
        return ClassificationDTO.fromDict(
            self._apiClient.get(f"/classifications/{idClassification}")
        )

    def createClassificationFromForm(self, form: MultiDict) -> None:
        minAge = FormParser.requiredInteger(form, "minAge", "Âge minimum")
        if minAge < 0:
            raise InvalidRequestError("L'âge minimum ne peut pas être négatif.")
        classification = ClassificationDTO(
            idClassification=0,
            minAge=minAge,
        )
        payload = classification.toDict()
        payload.pop("idClassification", None)
        self._apiClient.post("/classifications", payload)

    def updateClassificationFromForm(
        self, existing: ClassificationDTO, form: MultiDict
    ) -> ClassificationDTO:
        minAge = FormParser.requiredInteger(form, "minAge", "Âge minimum")
        if minAge < 0:
            raise InvalidRequestError("L'âge minimum ne peut pas être négatif.")
        classification = ClassificationDTO(
            idClassification=existing.idClassification,
            minAge=minAge,
        )
        return ClassificationDTO.fromDict(
            self._apiClient.put(
                f"/classifications/{existing.idClassification}",
                classification.toDict(),
            )
        )

    def deleteClassification(self, idClassification: int) -> None:
        self._apiClient.delete(f"/classifications/{idClassification}")