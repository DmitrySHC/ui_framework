from typing import Self

from ui_framework import BaseAssert, BaseDriver

from demo.steps.auth import AuthSteps

__all__ = ["AuthAsserts"]


class AuthAsserts(BaseAssert):
    def __init__(self, driver: BaseDriver, base_url: str) -> None:
        super().__init__(driver, base_url)
        self.step = AuthSteps(driver, base_url)

    def logged_in(self) -> Self:
        heading = self.step.secure_heading()
        assert "Secure Area" in heading, f"expected heading Secure Area, got {heading!r}"
        return self

    def logged_out(self) -> Self:
        heading = self.step.login_heading()
        assert "Login Page" in heading, f"expected Login Page, got {heading!r}"
        current_url = self.step.current_url()
        assert "/login" in current_url, f"expected /login, got {current_url!r}"
        return self

    def flash_contains(self, text: str) -> Self:
        flash = self.step.flash_text()
        assert text.lower() in flash.lower(), f"{text!r} not in flash {flash!r}"
        return self
