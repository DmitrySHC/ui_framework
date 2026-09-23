from typing import Self

from ui_framework import BaseDriver, BaseStep, readonly

from demo.pages import TablesPage

__all__ = ["TablesSteps"]


class TablesSteps(BaseStep):
    def __init__(self, driver: BaseDriver, base_url: str) -> None:
        super().__init__(driver, base_url)
        self.page = TablesPage(driver, base_url)

    def open(self) -> Self:
        self.page.open()
        return self

    def delete_smith(self) -> Self:
        self.page.delete_smith()
        return self

    @readonly
    def smith_email(self) -> str:
        return self.page.smith_email()

    @readonly
    def doe_due(self) -> str:
        return self.page.doe_due()

    @readonly
    def heading(self) -> str:
        return self.page.heading_text()

    @readonly
    def current_url(self) -> str:
        return self.page.current_url
