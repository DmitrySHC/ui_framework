from ..driver.exceptions import FrameworkError

__all__ = ["ConditionNotMatchedException", "ElementError"]


class ElementError(FrameworkError):
    """The element has the wrong locator, or it is used without a page."""


class ConditionNotMatchedException(FrameworkError):
    """A wait did not see the expected element state in time."""
