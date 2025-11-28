import gettext
from collections import OrderedDict
from collections.abc import Iterator, Sequence
from contextlib import suppress
from dataclasses import dataclass
from pathlib import Path

from babel import Locale
from babel.support import Translations
from injection import injectable

from src.services.i18n.abc import I18NService
from src.settings import Settings

_default_locale = Locale("en")


@dataclass(frozen=True)
class BabelService(I18NService):
    locale: Locale
    directories: Sequence[Path]
    domains: Sequence[str]

    def get_translations(self) -> gettext.NullTranslations:
        locales = OrderedDict.fromkeys((self.locale, _default_locale))
        stack = self.new_translations_stack(*locales.keys())
        translations = next(stack, gettext.NullTranslations())

        for next_translations in stack:
            translations.add_fallback(next_translations)

        return translations

    def new_translations_stack(self, *locales: Locale) -> Iterator[Translations]:
        for locale in locales:
            locale_str = str(locale)

            for directory in self.directories:
                for domain in self.domains:
                    with suppress(FileNotFoundError):
                        yield gettext.translation(
                            domain,
                            directory,
                            [locale_str],
                            Translations,
                        )


@injectable(on=I18NService)
def _babel_service_recipe(
    settings: Settings,
    locale: Locale = _default_locale,
) -> BabelService:
    return BabelService(
        locale=locale,
        directories=[settings.root_dir / "locales"],
        domains=["messages"],
    )
