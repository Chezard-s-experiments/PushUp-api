from datetime import datetime, timezone

from injection import injectable

from src.services.datetime.abc import DateTimeService


@injectable(on=DateTimeService)
class StdDateTimeService(DateTimeService):
    def now(self, tz: timezone | None = None) -> datetime:
        return datetime.now(tz)
