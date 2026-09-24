from typing import Self

from ui_framework import BaseAssert, BaseDriver, assert_that, equal_to

from demo.steps.dropdown import DropdownSteps

__all__ = ["DropdownAsserts"]


class DropdownAsserts(BaseAssert):
    def __init__(self, driver: BaseDriver, base_url: str) -> None:
        super().__init__(driver, base_url)
        self.step = DropdownSteps(driver, base_url)

    def verify_selected_is(self, option: str) -> Self:
        assert_that(self.step.selected(), equal_to(option))
        return self

    def verify_heading_is(self, text: str) -> Self:
        assert_that(self.step.heading(), equal_to(text))
        return self
