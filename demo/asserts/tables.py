from typing import Self

from ui_framework import BaseAssert, BaseDriver, assert_that, ends_with, equal_to

from demo.steps.tables import TablesSteps

__all__ = ["TablesAsserts"]


class TablesAsserts(BaseAssert):
    def __init__(self, driver: BaseDriver, base_url: str) -> None:
        super().__init__(driver, base_url)
        self.step = TablesSteps(driver, base_url)

    def smith_email_is(self, email: str) -> Self:
        assert_that(self.step.smith_email(), equal_to(email))
        return self

    def doe_due_is(self, due: str) -> Self:
        assert_that(self.step.doe_due(), equal_to(due))
        return self

    def heading_is(self, text: str) -> Self:
        assert_that(self.step.heading(), equal_to(text))
        return self

    def at_delete(self) -> Self:
        assert_that(self.step.current_url(), ends_with("#delete"))
        return self
