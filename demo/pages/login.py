from typing import Self

from ui_framework import BaseDriver, BasePage, Button, Text, TextInput, url

from .components import FlashMessage

__all__ = ["LoginPage"]


@url("/login")
class LoginPage(BasePage):
    heading = Text(css="h2")
    username = TextInput(id="username")
    password = TextInput(id="password")
    submit = Button(css="button[type='submit']")

    def __init__(self, driver: BaseDriver, base_url: str) -> None:
        super().__init__(driver, base_url)
        self.flash = FlashMessage(driver)

    def wait_loaded(self) -> Self:
        self.username.wait_visible()
        return self

    def sign_in(self, user: str, password: str) -> Self:
        self.username.fill(user)
        self.password.fill(password)
        self.submit.click()
        return self

    def heading_text(self) -> str:
        return self.heading.text

    def flash_text(self) -> str:
        return self.flash.message()
