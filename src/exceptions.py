from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import Any

from fastapi import status

from src.gettext import gettext as _


@dataclass(frozen=True)
class ApplicationError(Exception):
    message: str
    http_status: int = field(default=status.HTTP_400_BAD_REQUEST)
    details: Mapping[str, Any] = field(default_factory=dict)

    def __str__(self) -> str:
        return self.message

    def dump(self) -> dict[str, Any]:
        if details := self.details:
            return dict(details)

        return {"message": self.message}


class UnauthorizedError(ApplicationError):
    def __init__(self, message: str | None = None) -> None:
        super().__init__(
            message or _("unauthorized"),
            http_status=status.HTTP_401_UNAUTHORIZED,
        )


class ForbiddenError(ApplicationError):
    def __init__(self, message: str | None = None) -> None:
        super().__init__(
            message or _("forbidden"),
            http_status=status.HTTP_403_FORBIDDEN,
        )


class ConflictError(ApplicationError):
    def __init__(self, message: str) -> None:
        super().__init__(
            message,
            http_status=status.HTTP_409_CONFLICT,
        )
