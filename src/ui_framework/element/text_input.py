from typing import Self

from ..layers.scope import mutating
from .base import BaseElement

__all__ = ["TextInput"]


class TextInput(BaseElement):
    @mutating
    def fill(self, value: str, timeout: float | None = None) -> Self:
        self.wait_visible(timeout=timeout)
        self._locator().fill(value)
        return self

    @mutating
    def clear(self, timeout: float | None = None) -> Self:
        self.wait_visible(timeout=timeout)
        self._locator().clear()
        return self

    @property
    def value(self) -> str:
        self.wait_present()
        return self._locator().input_value()
