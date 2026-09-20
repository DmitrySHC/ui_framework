from typing import Self

from ..layers.scope import mutating
from .base import BaseElement

__all__ = ["RadioButton"]


class RadioButton(BaseElement):
    @property
    def is_selected(self) -> bool:
        self.wait_present()
        return self._locator().is_checked()

    @mutating
    def select(self, timeout: float | None = None) -> Self:
        """Выбирает кнопку; уже выбранную не кликает."""
        self.wait_clickable(timeout=timeout)
        self._locator().check()
        return self
