from src.exceptions import ConflictError


class EmailAlreadyUsedError(ConflictError):
    def __init__(self) -> None:
        super().__init__("Cette adresse e-mail est déjà utilisée.")
