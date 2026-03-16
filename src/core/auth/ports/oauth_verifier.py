from abc import abstractmethod
from typing import Protocol

from pydantic import BaseModel, EmailStr

from src.core.users.value_objects import OAuthProvider


class OAuthUserInfo(BaseModel):
    email: EmailStr
    provider_user_id: str
    first_name: str | None = None
    last_name: str | None = None


class OAuthVerifier(Protocol):
    @abstractmethod
    async def verify(self, provider: OAuthProvider, token: str) -> OAuthUserInfo:
        """Vérifie un token OAuth auprès du provider et retourne les infos utilisateur."""
        raise NotImplementedError
