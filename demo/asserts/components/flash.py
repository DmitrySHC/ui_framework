from typing import Self

from ui_framework import BaseComponentAsserts, BaseDriver, assert_that, contains_string

from demo.steps.components.flash import FlashComponentSteps

__all__ = ["FlashComponentAsserts"]


class FlashComponentAsserts(BaseComponentAsserts):
    def __init__(self, driver: BaseDriver, base_url: str) -> None:
        super().__init__(driver, base_url)
        self.step = FlashComponentSteps(driver, base_url)

    def verify_contains(self, text: str) -> Self:
        assert_that(self.step.text().lower(), contains_string(text.lower()))
        return self

    def verify_is_absent(self) -> Self:
        self.check(self.step.wait_absent)
        return self
