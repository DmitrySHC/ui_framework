from ..driver.base import BaseDriver
from ..layers.base import Layered
from ..layers.scope import ensure_inside_elements

__all__ = ["BaseInstance"]


class BaseInstance(Layered):
    """Something bound to a driver. Pages and components share this base."""

    def __init__(self, driver: BaseDriver) -> None:
        self._driver = driver

    @property
    def driver(self) -> BaseDriver:
        """The driver. Inside the step layer only page and component methods may use it."""
        if self._layered:
            ensure_inside_elements(f"{type(self).__name__}.driver")
        return self._driver
