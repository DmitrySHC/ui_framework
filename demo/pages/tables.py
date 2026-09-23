from typing import Self

from ui_framework import BasePage, Text, url

from .elements import PersonRow

__all__ = ["TablesPage"]


@url("/tables")
class TablesPage(BasePage):
    heading = Text(css="h3")
    smith = PersonRow(css='#table2 tbody tr:has(td.last-name:text-is("Smith"))')
    doe = PersonRow(css='#table2 tbody tr:has(td.last-name:text-is("Doe"))')

    def wait_loaded(self) -> Self:
        self.smith.wait_visible()
        return self

    def smith_email(self) -> str:
        return self.smith.email()

    def doe_due(self) -> str:
        return self.doe.due()

    def delete_smith(self) -> Self:
        self.smith.delete()
        return self

    def heading_text(self) -> str:
        return self.heading.text
