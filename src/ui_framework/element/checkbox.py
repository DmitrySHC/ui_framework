from typing import Self

from ..layers.scope import mutating
from .base import BaseElement

__all__ = ["Checkbox"]


class Checkbox(BaseElement):
    _role = "checkbox"
    @property
    def is_checked(self) -> bool:
        self.wait_present()
        return self._locator().is_checked()

    @mutating
    def set_checked(self, checked: bool, timeout: float | None = None) -> Self:
        """Sets the checkbox. Does nothing when it is already in that state."""
        self.wait_clickable(timeout=timeout)
        self._locator().set_checked(checked)
        return self

    def check(self, timeout: float | None = None) -> Self:
        return self.set_checked(True, timeout=timeout)

    def uncheck(self, timeout: float | None = None) -> Self:
        return self.set_checked(False, timeout=timeout)
