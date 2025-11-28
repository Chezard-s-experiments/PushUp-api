from enum import StrEnum, auto

from injection import mod


class Profile(StrEnum):
    DEFAULT = mod().name
    DEV = "dev"
    TEST = "test"


class SubProfile(StrEnum):
    GLOBAL = auto()


class Scope(StrEnum):
    LIFESPAN = auto()
    REQUEST = auto()
