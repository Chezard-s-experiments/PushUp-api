from abc import abstractmethod
from gettext import NullTranslations
from typing import Protocol


class I18NService(Protocol):
    @abstractmethod
    def get_translations(self) -> NullTranslations:
        raise NotImplementedError
