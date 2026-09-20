from typing import Self

from ui_framework import BasePage, Checkbox, Text, url

__all__ = ["CheckboxesPage"]


@url("/checkboxes")
class CheckboxesPage(BasePage):
    heading = Text(css="h3")
    first = Checkbox(css="#checkboxes input:nth-of-type(1)")
    second = Checkbox(css="#checkboxes input:nth-of-type(2)")

    def wait_loaded(self) -> Self:
        self.first.wait_visible()
        return self

    def set_states(self, first: bool, second: bool) -> Self:
        self.first.set_checked(first)
        self.second.set_checked(second)
        return self

    def states(self) -> tuple[bool, bool]:
        return self.first.is_checked, self.second.is_checked
