from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerificationError
from injection import injectable

from src.services.hasher.abc import Hasher


@injectable(on=Hasher)
class Argon2Hasher(Hasher):
    def __init__(self) -> None:
        self.__internal = PasswordHasher()

    def hash(self, value: str) -> str:
        return self.__internal.hash(value)

    def verify(self, value: str, hashed_value: str) -> bool:
        try:
            return self.__internal.verify(hashed_value, value)
        except (InvalidHashError, VerificationError):
            return False

    def needs_rehash(self, hashed_value: str) -> bool:
        return self.__internal.check_needs_rehash(hashed_value)
