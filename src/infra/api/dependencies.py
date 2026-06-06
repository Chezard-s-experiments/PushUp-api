from typing import Annotated, Any
from uuid import UUID

from babel import Locale
from fastapi import Depends, Header, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from injection.ext.fastapi import Inject

from src.services.jwt.abc import JWTService


async def get_access_token(
    authorization: Annotated[HTTPAuthorizationCredentials, Depends(HTTPBearer())],
) -> str:
    return authorization.credentials


async def get_identity_data(
    access_token: Annotated[str, Depends(get_access_token)],
    jwt: Inject[JWTService],
) -> dict[str, Any]:
    payload = jwt.decode(access_token)

    if payload.get("type") != "access":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    return payload


async def get_claimant_id(
    identity_data: Annotated[dict[str, Any], Depends(get_identity_data)],
) -> UUID:
    return UUID(identity_data["user_id"])


def _parse_accept_language(value: str) -> Locale | None:
    primary = value.split(",")[0].split(";")[0].strip().replace("_", "-")
    if not primary:
        return None

    try:
        return Locale.parse(primary, sep="-")
    except Exception:
        return None


async def get_locale(
    locale: Annotated[str | None, Header(alias="Accept-Language")] = None,
) -> Locale | None:
    if locale is None:
        return None

    return _parse_accept_language(locale)


async def require_auth(
    _: Annotated[dict[str, Any], Depends(get_identity_data)],
) -> None:
    return
