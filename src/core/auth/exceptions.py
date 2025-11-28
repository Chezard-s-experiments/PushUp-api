from src.exceptions import UnauthorizedError


class InvalidCredentialsError(UnauthorizedError):
    def __init__(self) -> None:
        super().__init__("Identifiants invalides.")
