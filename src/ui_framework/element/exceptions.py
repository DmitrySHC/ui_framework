from ..driver.exceptions import FrameworkError

__all__ = ["ConditionNotMatchedException", "ElementError"]


class ElementError(FrameworkError):
    """Элемент объявлен не с одним локатором или используется без страницы-владельца."""


class ConditionNotMatchedException(FrameworkError):
    """``wait_*`` не дождался состояния элемента за отведённое время."""
