from dataclasses import dataclass

import httpx
from injection import injectable
from pydantic import BaseModel, EmailStr

from src.core.auth.ports.oauth_verifier import OAuthUserInfo, OAuthVerifier
from src.core.users.value_objects import OAuthProvider


class _GoogleTokenInfo(BaseModel):
    """Schéma minimal de la réponse Google tokeninfo."""

    email: EmailStr
    sub: str
    given_name: str | None = None
    family_name: str | None = None


@injectable(on=OAuthVerifier)
@dataclass(frozen=True)
class GoogleOAuthVerifier(OAuthVerifier):
    """Vérification des tokens OAuth Google via l'endpoint tokeninfo."""

    async def verify(self, provider: OAuthProvider, token: str) -> OAuthUserInfo:
        if provider is not OAuthProvider.GOOGLE:
            raise ValueError(f"Provider non supporté: {provider}")

        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://oauth2.googleapis.com/tokeninfo",
                params={"id_token": token},
                timeout=5.0,
            )
            response.raise_for_status()
            data = _GoogleTokenInfo.model_validate_json(response.text)

        return OAuthUserInfo(
            email=data.email,
            provider_user_id=data.sub,
            first_name=data.given_name,
            last_name=data.family_name,
        )
