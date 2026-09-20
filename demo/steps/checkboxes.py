from typing import Self

from ui_framework import BaseDriver, BaseStep, readonly

from demo.pages import CheckboxesPage

__all__ = ["CheckboxesSteps"]


class CheckboxesSteps(BaseStep):
    def __init__(self, driver: BaseDriver, base_url: str) -> None:
        super().__init__(driver, base_url)
        self.page = CheckboxesPage(driver, base_url)

    def open(self) -> Self:
        self.page.open()
        return self

    def set_states(self, first: bool, second: bool) -> Self:
        self.page.set_states(first, second)
        return self

    @readonly
    def states(self) -> tuple[bool, bool]:
        return self.page.states()
