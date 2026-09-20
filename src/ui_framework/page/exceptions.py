from ..driver.exceptions import FrameworkError

__all__ = ["PageError"]


class PageError(FrameworkError):
    """Страница без ``@url`` или ``@url`` на классе, который не наследует ``BasePage``."""
