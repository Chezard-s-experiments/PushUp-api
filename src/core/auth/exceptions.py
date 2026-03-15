from src.exceptions import UnauthorizedError


class InvalidCredentialsError(UnauthorizedError):
    def __init__(self) -> None:
        super().__init__("Identifiants invalides.")


class InvalidRefreshTokenError(UnauthorizedError):
    def __init__(self) -> None:
        super().__init__("Refresh token invalide ou expiré.")
