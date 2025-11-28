from abc import abstractmethod
from datetime import timedelta
from typing import Any, Protocol


class JWTService(Protocol):
    @abstractmethod
    def decode(self, token: str) -> dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    def encode(self, payload: dict[str, Any], lifespan: timedelta = ...) -> str:
        raise NotImplementedError
