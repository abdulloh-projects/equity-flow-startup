from abc import ABC, abstractmethod

from app.startupp.models import DocType, Documents
from app.startupp.services.document_adapter import IStorageAdapter


class BaseDocument(ABC):
    doc_type: str

    def __init__(self, title: str, file_identifier: str, storage: IStorageAdapter):
        self.title = title
        self.file_url = storage.get_url(file_identifier)

    @abstractmethod
    def get_metadata(self) -> dict: ...

    def save(self) -> Documents:
        return Documents.objects.create(
            doc_type=self.doc_type,
            title=self.title,
            file_url=self.file_url,
        )


class FinancialReportDocument(BaseDocument):
    doc_type = DocType.FINANCIAL_REPORT

    def get_metadata(self) -> dict:
        return {"type": self.doc_type, "category": "finance"}


class BusinessPlanDocument(BaseDocument):
    doc_type = DocType.BUSSINESS_PLAN

    def get_metadata(self) -> dict:
        return {"type": self.doc_type, "category": "strategy"}


class PresentationDocument(BaseDocument):
    doc_type = DocType.PRESENTATION

    def get_metadata(self) -> dict:
        return {"type": self.doc_type, "category": "pitch"}


class LegalDocument(BaseDocument):
    doc_type = DocType.LEGAL_DOCUMENT

    def get_metadata(self) -> dict:
        return {"type": self.doc_type, "category": "legal"}


class DocumentFactory:
    _registry: dict[str, type[BaseDocument]] = {
        DocType.FINANCIAL_REPORT: FinancialReportDocument,
        DocType.BUSSINESS_PLAN: BusinessPlanDocument,
        DocType.PRESENTATION: PresentationDocument,
        DocType.LEGAL_DOCUMENT: LegalDocument,
    }

    @classmethod
    def create(
        cls,
        doc_type: str,
        title: str,
        file_identifier: str,
        storage: IStorageAdapter,
    ) -> BaseDocument:
        doc_class = cls._registry.get(doc_type)
        if not doc_class:
            raise ValueError(f"Unknown document type: '{doc_type}'")
        return doc_class(title=title, file_identifier=file_identifier, storage=storage)
