from typing import Self

from ui_framework import BaseAssert, BaseDriver, assert_that, contains_string

from demo.asserts.components import FlashComponentAsserts
from demo.steps.auth import AuthSteps

__all__ = ["AuthAsserts"]


class AuthAsserts(BaseAssert):
    def __init__(self, driver: BaseDriver, base_url: str) -> None:
        super().__init__(driver, base_url)
        self.step = AuthSteps(driver, base_url)
        self.flash = FlashComponentAsserts(driver, base_url)

    def verify_logged_in(self) -> Self:
        assert_that(self.step.secure_heading(), contains_string("Secure Area"))
        return self

    def verify_logged_out(self) -> Self:
        assert_that(self.step.login_heading(), contains_string("Login Page"))
        assert_that(self.current_url(), contains_string("/login"))
        return self
