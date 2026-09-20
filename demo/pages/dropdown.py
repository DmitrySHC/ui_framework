from typing import Self

from ui_framework import BasePage, Select, Text, url

__all__ = ["DropdownPage"]


@url("/dropdown")
class DropdownPage(BasePage):
    heading = Text(css="h3")
    menu = Select(id="dropdown")

    def wait_loaded(self) -> Self:
        self.menu.wait_visible()
        return self

    def choose(self, option: str) -> Self:
        self.menu.select_by_text(option)
        return self

    def selected(self) -> str:
        return self.menu.selected_text

    def heading_text(self) -> str:
        return self.heading.text
