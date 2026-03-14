from datetime import UTC, datetime, timezone
from uuid import UUID

import pytest
from pydantic import SecretStr

from src.core.auth.commands.login_user import LoginUserCommand, LoginUserHandler
from src.core.auth.dtos.tokens import AccessTokenPayload
from src.core.auth.exceptions import InvalidCredentialsError
from src.core.users.aggregates import User
from src.core.users.ports.repo import UserRepository
from src.core.users.value_objects import Email
from src.services.datetime.abc import DateTimeService
from src.services.hasher.argon2 import Argon2Hasher
from src.services.jwt.pyjwt import PyJWTService
from src.services.uuid.abc import UUIDGenerator


class FakeDateTime(DateTimeService):
    def __init__(self) -> None:
        # utilise une date suffisamment éloignée pour éviter les expirations lors de l'exécution des tests
        self.value = datetime(2100, 1, 1, tzinfo=UTC)

    def now(self, tz: timezone = UTC) -> datetime:
        return self.value.astimezone(tz)


class FakeUUID(UUIDGenerator):
    def next(self) -> UUID:
        return UUID(int=1)


class InMemoryUserRepository(UserRepository):
    def __init__(self, user: User | None = None) -> None:
        self._user = user

    async def add(self, user: User) -> None:
        self._user = user

    async def update(self, user: User) -> None:
        self._user = user

    async def get_by_email(self, email: str) -> User | None:
        if self._user and str(self._user.email) == email:
            return self._user
        return None

    async def get_by_id(self, user_id: UUID) -> User | None:
        if self._user and self._user.id == user_id:
            return self._user
        return None


def make_user(hasher: Argon2Hasher) -> User:
    return User(
        id=UUID(int=1),
        email=Email("john@example.com"),
        hashed_password=SecretStr(hasher.hash("s3cret!")),
        first_name="John",
        last_name="Doe",
        created_at=datetime(2025, 1, 1, tzinfo=UTC),
        updated_at=datetime(2025, 1, 1, tzinfo=UTC),
    )


@pytest.mark.asyncio()
async def test_login_user_returns_access_token() -> None:
    hasher = Argon2Hasher()
    user = make_user(hasher)
    repo = InMemoryUserRepository(user)
    datetime_service = FakeDateTime()
    jwt_service = PyJWTService(datetime_service, "secret")
    handler = LoginUserHandler(datetime_service, hasher, jwt_service, repo)

    command = LoginUserCommand(email=str(user.email), password=SecretStr("s3cret!"))
    tokens = await handler.handle(command)

    assert isinstance(tokens, AccessTokenPayload)
    decoded = jwt_service.decode(tokens.access_token)
    assert decoded["user_id"] == str(user.id)


@pytest.mark.asyncio()
async def test_login_user_with_bad_password_raises() -> None:
    hasher = Argon2Hasher()
    user = make_user(hasher)
    repo = InMemoryUserRepository(user)
    datetime_service = FakeDateTime()
    jwt_service = PyJWTService(datetime_service, "secret")
    handler = LoginUserHandler(datetime_service, hasher, jwt_service, repo)

    with pytest.raises(InvalidCredentialsError):
        await handler.handle(
            LoginUserCommand(email=str(user.email), password=SecretStr("wrong")),
        )
