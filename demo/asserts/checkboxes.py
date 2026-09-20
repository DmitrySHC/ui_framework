from typing import Self

from ui_framework import BaseAssert, BaseDriver

from demo.steps.checkboxes import CheckboxesSteps

__all__ = ["CheckboxesAsserts"]


class CheckboxesAsserts(BaseAssert):
    def __init__(self, driver: BaseDriver, base_url: str) -> None:
        super().__init__(driver, base_url)
        self.step = CheckboxesSteps(driver, base_url)

    def states_are(self, first: bool, second: bool) -> Self:
        states = self.step.states()
        assert states == (first, second), f"states {states}, expected {(first, second)}"
        return self
