"""Value Object HashedPassword : mot de passe hashé, immuable, vérifiable."""

from __future__ import annotations

from pydantic import BaseModel, SecretStr

from src.services.hasher.abc import Hasher


class HashedPassword(BaseModel):
    """Value Object représentant un mot de passe déjà hashé (Argon2/bcrypt)."""

    value: SecretStr

    model_config = {"frozen": True}

    @classmethod
    def from_hash(cls, hashed: str) -> HashedPassword:
        """Construit le VO à partir d'une chaîne déjà hashée (création ou chargement DB)."""
        return cls(value=SecretStr(hashed))

    def get_secret_value(self) -> str:
        """Retourne le hash pour persistance ou vérification. À ne pas logger."""
        return self.value.get_secret_value()

    def verify(self, plain: str, hasher: Hasher) -> bool:
        """Vérifie qu'un mot de passe en clair correspond à ce hash."""
        return hasher.verify(plain, self.get_secret_value())

    def needs_rehash(self, hasher: Hasher) -> bool:
        """Indique si le hash doit être recalculé (paramètres algo obsolètes)."""
        return hasher.needs_rehash(self.get_secret_value())
