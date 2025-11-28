from abc import abstractmethod
from typing import Protocol


class Hasher(Protocol):
    @abstractmethod
    def hash(self, value: str) -> str:
        raise NotImplementedError

    @abstractmethod
    def verify(self, value: str, hashed_value: str) -> bool:
        raise NotImplementedError

    def needs_rehash(self, hashed_value: str) -> bool:  # pragma: no cover
        return False
