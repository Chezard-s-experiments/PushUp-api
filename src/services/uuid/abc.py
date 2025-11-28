from abc import abstractmethod
from typing import Protocol
from uuid import UUID


class UUIDGenerator(Protocol):
    @abstractmethod
    def next(self) -> UUID:
        raise NotImplementedError
