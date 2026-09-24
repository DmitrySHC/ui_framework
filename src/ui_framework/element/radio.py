from typing import Self

from ..layers.scope import mutating
from .base import BaseElement

__all__ = ["RadioButton"]


class RadioButton(BaseElement):
    _role = "radio"
    @property
    def is_selected(self) -> bool:
        self.wait_present()
        return self._locator().is_checked()

    @mutating
    def select(self, timeout: float | None = None) -> Self:
        """Selects the button. An already selected one is left alone."""
        self.wait_clickable(timeout=timeout)
        self._locator().check()
        return self
