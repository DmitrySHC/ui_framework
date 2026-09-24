from typing import Self

from ui_framework import BaseAssert, BaseDriver, assert_that, equal_to

from demo.steps.checkboxes import CheckboxesSteps

__all__ = ["CheckboxesAsserts"]


class CheckboxesAsserts(BaseAssert):
    def __init__(self, driver: BaseDriver, base_url: str) -> None:
        super().__init__(driver, base_url)
        self.step = CheckboxesSteps(driver, base_url)

    def verify_states_are(self, first: bool, second: bool) -> Self:
        assert_that(self.step.states(), equal_to((first, second)))
        return self
