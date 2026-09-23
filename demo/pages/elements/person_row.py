from typing import Self

from ui_framework import BaseElement, mutating

__all__ = ["PersonRow"]


class PersonRow(BaseElement):
    """Строка таблицы: один локатор на ``tr``, ячейки и ссылки ищутся от него."""

    def email(self) -> str:
        self.wait_present()
        return self._locator().locator("td.email").inner_text()

    def due(self) -> str:
        self.wait_present()
        return self._locator().locator("td.dues").inner_text()

    @mutating
    def delete(self) -> Self:
        self.wait_visible()
        self._locator().locator("a[href='#delete']").click()
        return self
