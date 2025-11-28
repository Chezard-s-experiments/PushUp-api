from abc import abstractmethod
from datetime import UTC, datetime, timezone
from typing import Protocol


class DateTimeService(Protocol):
    @abstractmethod
    def now(self, tz: timezone = ...) -> datetime:
        raise NotImplementedError

    def utcnow(self) -> datetime:
        return self.now(UTC)
