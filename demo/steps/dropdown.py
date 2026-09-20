from typing import Self

from ui_framework import BaseDriver, BaseStep, readonly

from demo.pages import DropdownPage

__all__ = ["DropdownSteps"]


class DropdownSteps(BaseStep):
    def __init__(self, driver: BaseDriver, base_url: str) -> None:
        super().__init__(driver, base_url)
        self.page = DropdownPage(driver, base_url)

    def choose(self, option: str) -> Self:
        self.page.open().choose(option)
        return self

    @readonly
    def selected(self) -> str:
        return self.page.selected()

    @readonly
    def heading(self) -> str:
        return self.page.heading_text()
