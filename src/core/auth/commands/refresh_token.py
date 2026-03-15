from datetime import timedelta
from typing import NamedTuple

from cq import command_handler
from jwt import InvalidTokenError
from pydantic import BaseModel

from src.core.auth.dtos.tokens import AccessTokenPayload
from src.core.auth.exceptions import InvalidRefreshTokenError
from src.services.jwt.abc import JWTService

ACCESS_TOKEN_LIFESPAN = timedelta(hours=1)
REFRESH_TOKEN_LIFESPAN = timedelta(days=7)


class RefreshTokenCommand(BaseModel):
    refresh_token: str


@command_handler
class RefreshTokenHandler(NamedTuple):
    jwt: JWTService

    async def handle(self, command: RefreshTokenCommand) -> AccessTokenPayload:
        try:
            payload = self.jwt.decode(command.refresh_token)
        except InvalidTokenError as exc:
            raise InvalidRefreshTokenError() from exc

        if payload.get("type") != "refresh":
            raise InvalidRefreshTokenError()

        claims = {"user_id": payload["user_id"], "email": payload["email"]}

        access_token = self.jwt.encode(
            {**claims, "type": "access"},
            lifespan=ACCESS_TOKEN_LIFESPAN,
        )
        refresh_token = self.jwt.encode(
            {**claims, "type": "refresh"},
            lifespan=REFRESH_TOKEN_LIFESPAN,
        )

        return AccessTokenPayload(
            access_token=access_token,
            refresh_token=refresh_token,
        )
