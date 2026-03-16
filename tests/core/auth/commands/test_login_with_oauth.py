from datetime import UTC, datetime, timezone
from uuid import UUID

import pytest
from pydantic import SecretStr

from src.core.auth.commands.login_with_oauth import (
    LoginWithOAuthCommand,
    LoginWithOAuthHandler,
)
from src.core.auth.dtos.tokens import AccessTokenPayload
from src.core.auth.ports.oauth_verifier import OAuthUserInfo, OAuthVerifier
from src.core.users.aggregates import User
from src.core.users.ports.repo import UserRepository
from src.core.users.value_objects import Email, HashedPassword, OAuthProvider
from src.services.datetime.abc import DateTimeService
from src.services.hasher.argon2 import Argon2Hasher
from src.services.jwt.pyjwt import PyJWTService
from src.services.uuid.abc import UUIDGenerator


class FakeDateTime(DateTimeService):
    def __init__(self) -> None:
        self.value = datetime(2100, 1, 1, tzinfo=UTC)

    def now(self, tz: timezone = UTC) -> datetime:
        return self.value.astimezone(tz)


class FakeUUID(UUIDGenerator):
    def __init__(self) -> None:
        self._next = UUID(int=1)

    def next(self) -> UUID:
        return self._next


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


class FakeOAuthVerifier(OAuthVerifier):
    async def verify(self, provider: OAuthProvider, token: str) -> OAuthUserInfo:
        assert provider == OAuthProvider.GOOGLE
        assert token == "oauth-token"

        return OAuthUserInfo(
            email="john@example.com",
            provider_user_id="google-123",
            first_name="John",
            last_name="Doe",
        )


def _make_handler(user: User | None = None) -> LoginWithOAuthHandler:
    hasher = Argon2Hasher()
    repo = InMemoryUserRepository(user)
    datetime_service = FakeDateTime()
    jwt_service = PyJWTService(datetime_service, "secret")
    uuid = FakeUUID()
    verifier = FakeOAuthVerifier()
    return LoginWithOAuthHandler(
        datetime=datetime_service,
        hasher=hasher,
        jwt=jwt_service,
        repo=repo,
        uuid=uuid,
        verifier=verifier,
    )


@pytest.mark.asyncio()
async def test_login_with_oauth_creates_user_if_not_exists() -> None:
    handler = _make_handler()

    command = LoginWithOAuthCommand(
        provider=OAuthProvider.GOOGLE,
        token=SecretStr("oauth-token"),
    )
    tokens = await handler.handle(command)

    assert isinstance(tokens, AccessTokenPayload)


@pytest.mark.asyncio()
async def test_login_with_oauth_links_existing_user_by_email() -> None:
    hasher = Argon2Hasher()
    existing_user = User(
        id=UUID(int=1),
        email=Email("john@example.com"),
        hashed_password=HashedPassword.from_hash(hasher.hash("s3cret!")),
        first_name=None,
        last_name=None,
        oauth_provider=None,
        oauth_id=None,
        created_at=datetime(2025, 1, 1, tzinfo=UTC),
        updated_at=datetime(2025, 1, 1, tzinfo=UTC),
    )

    handler = _make_handler(existing_user)

    command = LoginWithOAuthCommand(
        provider=OAuthProvider.GOOGLE,
        token=SecretStr("oauth-token"),
    )
    tokens = await handler.handle(command)

    assert isinstance(tokens, AccessTokenPayload)
