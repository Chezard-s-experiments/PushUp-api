"""Value Object OAuthProvider : fournisseur OAuth typé (google, apple)."""

from __future__ import annotations

from enum import Enum


class OAuthProvider(str, Enum):
    """Fournisseur OAuth supporté par le domaine utilisateurs."""

    GOOGLE = "google"
    APPLE = "apple"

    def __str__(self) -> str:
        return self.value

