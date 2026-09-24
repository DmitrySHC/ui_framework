from ..driver.exceptions import FrameworkError

__all__ = ["PageError"]


class PageError(FrameworkError):
    """A page is missing its url decorator, or the decorator is on the wrong class."""
