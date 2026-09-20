from ..driver.base import BaseDriver
from ..layers.base import Layered
from ..layers.scope import ensure_inside_elements

__all__ = ["BaseInstance"]


class BaseInstance(Layered):
    """Объект, привязанный к драйверу: общий предок страниц и компонентов."""

    def __init__(self, driver: BaseDriver) -> None:
        self._driver = driver

    @property
    def driver(self) -> BaseDriver:
        """Драйвер; если объект создан внутри слоя шагов, доступен только из методов страниц и компонентов."""
        if self._layered:
            ensure_inside_elements(f"{type(self).__name__}.driver")
        return self._driver
