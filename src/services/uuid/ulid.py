from uuid import UUID

from injection import injectable
from ulid import ULID

from src.services.uuid.abc import UUIDGenerator


@injectable(on=UUIDGenerator)
class ULIDGenerator(UUIDGenerator):
    def next(self) -> UUID:
        return ULID().to_uuid()
