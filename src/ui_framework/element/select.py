from typing import Self

from ..layers.scope import mutating
from .base import BaseElement

__all__ = ["Select"]

_SELECTED_OPTION = "option:checked"


class Select(BaseElement):
    @mutating
    def select_by_text(self, text: str, timeout: float | None = None) -> Self:
        self.wait_visible(timeout=timeout)
        self._locator().select_option(label=text)
        return self

    @mutating
    def select_by_value(self, value: str, timeout: float | None = None) -> Self:
        self.wait_visible(timeout=timeout)
        self._locator().select_option(value=value)
        return self

    @property
    def selected_text(self) -> str:
        self.wait_present()
        return self._locator().locator(_SELECTED_OPTION).inner_text()
