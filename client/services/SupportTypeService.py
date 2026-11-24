from typing import List

from werkzeug.datastructures import MultiDict

from exceptions import InvalidRequestError
from models import SupportTypeDTO

from .ApiClient import ApiClient
from .FormParser import FormParser


class SupportTypeService:
    def __init__(self, apiClient: ApiClient) -> None:
        self._apiClient = apiClient

    def getAllSupportTypes(self) -> List[SupportTypeDTO]:
        data = self._apiClient.get("/support-types")
        return [SupportTypeDTO.fromDict(item) for item in data]

    def getSupportTypeById(self, idSupportType: int) -> SupportTypeDTO:
        return SupportTypeDTO.fromDict(
            self._apiClient.get(f"/support-types/{idSupportType}")
        )

    def createSupportTypeFromForm(self, form: MultiDict) -> None:
        supportType = self._supportTypeFromForm(form)
        payload = supportType.toDict()
        payload.pop("idSupportType", None)
        self._apiClient.post("/support-types", payload)

    def updateSupportTypeFromForm(
        self, existing: SupportTypeDTO, form: MultiDict
    ) -> SupportTypeDTO:
        supportType = self._supportTypeFromForm(form)
        supportType.idSupportType = existing.idSupportType
        return SupportTypeDTO.fromDict(
            self._apiClient.put(
                f"/support-types/{existing.idSupportType}",
                supportType.toDict(),
            )
        )

    def deleteSupportType(self, idSupportType: int) -> None:
        self._apiClient.delete(f"/support-types/{idSupportType}")

    @staticmethod
    def _supportTypeFromForm(form: MultiDict) -> SupportTypeDTO:
        name = FormParser.text(form, "name", "Nom", required=True)
        mode = FormParser.text(form, "mode", "Mode", required=True)
        if mode not in {"physical", "digital"}:
            raise InvalidRequestError(
                "Le mode doit être « physical » ou « digital »."
            )
        return SupportTypeDTO(idSupportType=0, name=name, mode=mode)
