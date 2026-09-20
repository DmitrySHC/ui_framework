from typing import Self

from ui_framework import BaseDriver, BasePage, Link, Text, url

from .components import FlashMessage

__all__ = ["SecurePage"]


@url("/secure")
class SecurePage(BasePage):
    heading = Text(css="h2")
    logout = Link(css="a[href='/logout']")

    def __init__(self, driver: BaseDriver, base_url: str) -> None:
        super().__init__(driver, base_url)
        self.flash = FlashMessage(driver)

    def wait_loaded(self) -> Self:
        self.heading.wait_visible()
        return self

    def sign_out(self) -> Self:
        self.logout.click()
        return self

    def heading_text(self) -> str:
        return self.heading.text

    def flash_text(self) -> str:
        return self.flash.message()
