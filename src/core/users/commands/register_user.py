from typing import NamedTuple

from cq import command_handler
from pydantic import BaseModel, EmailStr, SecretStr, field_validator

from src.core.users.aggregates import User
from src.core.users.exceptions import EmailAlreadyUsedError
from src.core.users.ports.repo import UserRepository
from src.core.users.value_objects import Email
from src.services.datetime.abc import DateTimeService
from src.services.hasher.abc import Hasher
from src.services.uuid.abc import UUIDGenerator


class RegisterUserCommand(BaseModel):
    email: EmailStr
    password: SecretStr
    first_name: str | None = None
    last_name: str | None = None

    @field_validator("first_name", "last_name")
    @classmethod
    def _normalize_names(cls, value: str | None) -> str | None:
        if value is None:
            return value
        cleaned = value.strip()
        return cleaned or None


@command_handler
class RegisterUserHandler(NamedTuple):
    datetime: DateTimeService
    hasher: Hasher
    repo: UserRepository
    uuid: UUIDGenerator

    async def handle(self, command: RegisterUserCommand) -> User:
        if await self.repo.get_by_email(command.email):
            raise EmailAlreadyUsedError()

        now = self.datetime.utcnow()
        user = User(
            id=self.uuid.next(),
            email=Email(command.email),
            hashed_password=SecretStr(
                self.hasher.hash(command.password.get_secret_value())
            ),
            first_name=command.first_name,
            last_name=command.last_name,
            created_at=now,
            updated_at=now,
        )
        await self.repo.add(user)
        return user
