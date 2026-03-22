from src.exceptions import ApplicationError


class ProgramNotFoundError(ApplicationError):
    def __init__(self) -> None:
        super().__init__("Le programme demandé est introuvable.")
