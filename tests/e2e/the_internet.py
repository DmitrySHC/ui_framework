from typing import Self

from ui_framework import (
    BaseComponent,
    BasePage,
    Button,
    Link,
    Select,
    Text,
    TextInput,
    url,
)
from ui_framework.driver import BaseDriver

BASE_URL = "https://the-internet.herokuapp.com"


class FlashMessage(BaseComponent):
    banner = Text(id="flash")


class InternetPage(BasePage):
    def __init__(self, driver: BaseDriver, base_url: str) -> None:
        super().__init__(driver, base_url)
        self.flash = FlashMessage(driver)


@url("/login")
class LoginPage(InternetPage):
    heading = Text(css="h2")
    username = TextInput(id="username")
    password = TextInput(id="password")
    submit = Button(css="button[type='submit']")

    def wait_loaded(self) -> Self:
        self.username.wait_visible()
        return self


@url("/secure")
class SecurePage(InternetPage):
    heading = Text(css="h2")
    logout = Link(css="a[href='/logout']")

    def wait_loaded(self) -> Self:
        self.heading.wait_visible()
        return self


@url("/dropdown")
class DropdownPage(BasePage):
    heading = Text(css="h3")
    menu = Select(id="dropdown")

    def wait_loaded(self) -> Self:
        self.heading.wait_visible()
        return self


@url("/dropdown")
class StubbedPage(BasePage):
    heading = Text(id="stubbed")

    def wait_loaded(self) -> Self:
        self.heading.wait_visible()
        return self
