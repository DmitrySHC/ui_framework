from typing import Self

from ui_framework import BaseAssert, BaseDriver

from demo.steps.tables import TablesSteps

__all__ = ["TablesAsserts"]


class TablesAsserts(BaseAssert):
    def __init__(self, driver: BaseDriver, base_url: str) -> None:
        super().__init__(driver, base_url)
        self.step = TablesSteps(driver, base_url)

    def smith_email_is(self, email: str) -> Self:
        actual = self.step.smith_email()
        assert actual == email, f"email {actual!r}, expected {email!r}"
        return self

    def doe_due_is(self, due: str) -> Self:
        actual = self.step.doe_due()
        assert actual == due, f"due {actual!r}, expected {due!r}"
        return self

    def heading_is(self, text: str) -> Self:
        heading = self.step.heading()
        assert heading == text, f"heading {heading!r}, expected {text!r}"
        return self

    def at_delete(self) -> Self:
        url = self.step.current_url()
        assert url.endswith("#delete"), f"url {url!r} has no #delete"
        return self
