from typing import Self

from ui_framework import BaseAssert, BaseDriver

from demo.steps.dropdown import DropdownSteps

__all__ = ["DropdownAsserts"]


class DropdownAsserts(BaseAssert):
    def __init__(self, driver: BaseDriver, base_url: str) -> None:
        super().__init__(driver, base_url)
        self.step = DropdownSteps(driver, base_url)

    def selected_is(self, option: str) -> Self:
        selected = self.step.selected()
        assert selected == option, f"selected {selected!r}, expected {option!r}"
        return self

    def heading_is(self, text: str) -> Self:
        heading = self.step.heading()
        assert heading == text, f"heading {heading!r}, expected {text!r}"
        return self
