from typing import Self

from ui_framework import BaseDriver, BaseStep, readonly

from demo.pages import LoginPage, SecurePage
from demo.steps.components import FlashComponentSteps

__all__ = ["AuthSteps"]


class AuthSteps(BaseStep):
    """Вход через ``LoginPage`` и выход через ``SecurePage``."""

    def __init__(self, driver: BaseDriver, base_url: str) -> None:
        super().__init__(driver, base_url)
        self.login = LoginPage(driver, base_url)
        self.secure = SecurePage(driver, base_url)
        self.flash = FlashComponentSteps(driver, base_url)

    def open_login(self) -> Self:
        self.login.open()
        return self

    def login_as(self, user: str, password: str) -> Self:
        self.login.open().sign_in(user, password)
        return self

    def logout(self) -> Self:
        self.secure.wait_loaded().sign_out()
        return self

    @readonly
    def login_heading(self) -> str:
        return self.login.wait_loaded().heading_text()

    @readonly
    def secure_heading(self) -> str:
        return self.secure.wait_loaded().heading_text()

    @readonly
    def current_url(self) -> str:
        """URL текущей вкладки."""
        return self.login.current_url
