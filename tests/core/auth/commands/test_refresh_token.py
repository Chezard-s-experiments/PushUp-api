from datetime import UTC, datetime, timedelta, timezone

import pytest

from src.core.auth.commands.refresh_token import (
    RefreshTokenCommand,
    RefreshTokenHandler,
)
from src.core.auth.dtos.tokens import AccessTokenPayload
from src.core.auth.exceptions import InvalidRefreshTokenError
from src.services.datetime.abc import DateTimeService
from src.services.jwt.pyjwt import PyJWTService


class FakeDateTime(DateTimeService):
    def __init__(self) -> None:
        self.value = datetime(2100, 1, 1, tzinfo=UTC)

    def now(self, tz: timezone = UTC) -> datetime:
        return self.value.astimezone(tz)


def _make_jwt_service(dt: FakeDateTime | None = None) -> PyJWTService:
    return PyJWTService(dt or FakeDateTime(), "secret")


def _make_refresh_token(jwt: PyJWTService) -> str:
    return jwt.encode(
        {"user_id": "abc-123", "email": "john@example.com", "type": "refresh"},
        lifespan=timedelta(days=7),
    )


@pytest.mark.asyncio()
async def test_refresh_returns_new_token_pair() -> None:
    jwt = _make_jwt_service()
    handler = RefreshTokenHandler(jwt=jwt)

    refresh = _make_refresh_token(jwt)
    result = await handler.handle(RefreshTokenCommand(refresh_token=refresh))

    assert isinstance(result, AccessTokenPayload)
    assert result.access_token != refresh

    decoded_access = jwt.decode(result.access_token)
    assert decoded_access["type"] == "access"
    assert decoded_access["user_id"] == "abc-123"
    assert decoded_access["email"] == "john@example.com"

    decoded_refresh = jwt.decode(result.refresh_token)
    assert decoded_refresh["type"] == "refresh"
    assert decoded_refresh["user_id"] == "abc-123"


@pytest.mark.asyncio()
async def test_refresh_rejects_access_token() -> None:
    jwt = _make_jwt_service()
    handler = RefreshTokenHandler(jwt=jwt)

    access_token = jwt.encode(
        {"user_id": "abc-123", "email": "john@example.com", "type": "access"},
        lifespan=timedelta(hours=1),
    )

    with pytest.raises(InvalidRefreshTokenError):
        await handler.handle(RefreshTokenCommand(refresh_token=access_token))


@pytest.mark.asyncio()
async def test_refresh_rejects_invalid_token() -> None:
    jwt = _make_jwt_service()
    handler = RefreshTokenHandler(jwt=jwt)

    with pytest.raises(InvalidRefreshTokenError):
        await handler.handle(RefreshTokenCommand(refresh_token="not-a-jwt"))


@pytest.mark.asyncio()
async def test_refresh_rejects_expired_token() -> None:
    dt = FakeDateTime()
    dt.value = datetime(2020, 1, 1, tzinfo=UTC)
    jwt = _make_jwt_service(dt)

    refresh = jwt.encode(
        {"user_id": "abc-123", "email": "john@example.com", "type": "refresh"},
        lifespan=timedelta(seconds=1),
    )

    handler = RefreshTokenHandler(jwt=jwt)

    with pytest.raises(InvalidRefreshTokenError):
        await handler.handle(RefreshTokenCommand(refresh_token=refresh))
