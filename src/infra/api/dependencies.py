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
    return jwt.decode(access_token)


async def get_claimant_id(
    identity_data: Annotated[dict[str, Any], Depends(get_identity_data)],
) -> UUID:
    return UUID(identity_data["user_id"])


async def get_locale(
    locale: Annotated[str | None, Header(alias="Accept-Language")] = None,
) -> Locale | None:
    if locale is None:
        return None

    try:
        return Locale.parse(locale, sep="-")
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST) from exc


async def require_auth(
    _: Annotated[dict[str, Any], Depends(get_identity_data)],
) -> None:
    return
