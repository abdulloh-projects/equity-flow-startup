from abc import ABC, abstractmethod


class IStorageAdapter(ABC):
    @abstractmethod
    def get_url(self, identifier: str) -> str: ...


class CloudStorageAdapter(IStorageAdapter):
    def __init__(self, bucket: str, base_url: str):
        self.bucket = bucket
        self.base_url = base_url.rstrip("/")

    def get_url(self, identifier: str) -> str:
        return f"{self.base_url}/{identifier}"
