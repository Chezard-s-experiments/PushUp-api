"""Value Object Email : adresse email validée, immuable."""

from pydantic import EmailStr, RootModel


class Email(RootModel[EmailStr]):
    """Value Object représentant une adresse email avec validation de format."""

    def __str__(self) -> str:
        return self.root

    def __repr__(self) -> str:
        return f"Email({self.root!r})"
