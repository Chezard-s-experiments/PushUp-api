from injection import inject

from src.services.i18n.abc import I18NService


@inject
def gettext(msgid: str, service: I18NService = NotImplemented) -> str:
    return service.get_translations().gettext(msgid)
