from datetime import UTC, datetime, timezone
from uuid import UUID

import pytest
from pydantic import SecretStr

from src.core.users.aggregates import User
from src.core.users.commands.register_user import (
    RegisterUserCommand,
    RegisterUserHandler,
)
from src.core.users.exceptions import EmailAlreadyUsedError
from src.core.users.ports.repo import UserRepository
from src.services.datetime.abc import DateTimeService
from src.services.hasher.argon2 import Argon2Hasher
from src.services.uuid.abc import UUIDGenerator


class FakeDateTime(DateTimeService):
    def now(self, tz: timezone = UTC) -> datetime:
        return datetime(2025, 1, 1, tzinfo=tz)


class FakeUUID(UUIDGenerator):
    def __init__(self) -> None:
        self.value = UUID(int=1)

    def next(self) -> UUID:
        return self.value


class InMemoryUserRepository(UserRepository):
    def __init__(self) -> None:
        self._by_email: dict[str, User] = {}

    async def add(self, user: User) -> None:
        self._by_email[str(user.email)] = user

    async def update(self, user: User) -> None:
        self._by_email[str(user.email)] = user

    async def get_by_email(self, email: str) -> User | None:
        return self._by_email.get(email)

    async def get_by_id(self, user_id: UUID) -> User | None:
        for user in self._by_email.values():
            if user.id == user_id:
                return user
        return None


@pytest.mark.asyncio()
async def test_register_user_hashes_password() -> None:
    repo = InMemoryUserRepository()
    handler = RegisterUserHandler(FakeDateTime(), Argon2Hasher(), repo, FakeUUID())

    command = RegisterUserCommand(
        email="john@example.com",
        password=SecretStr("s3cret!"),
        first_name="John",
        last_name="Doe",
    )
    user = await handler.handle(command)

    assert str(user.email) == command.email
    assert (
        user.hashed_password.get_secret_value() != command.password.get_secret_value()
    )
    assert await repo.get_by_email(command.email) is not None


@pytest.mark.asyncio()
async def test_register_user_with_duplicate_email_raises_conflict() -> None:
    repo = InMemoryUserRepository()
    handler = RegisterUserHandler(FakeDateTime(), Argon2Hasher(), repo, FakeUUID())
    command = RegisterUserCommand(
        email="jane@example.com", password=SecretStr("pwd1234")
    )
    await handler.handle(command)

    with pytest.raises(EmailAlreadyUsedError):
        await handler.handle(command)
