from typing import Self

from ui_framework import BaseComponentSteps, BaseDriver, readonly

from demo.pages.components import FlashMessage

__all__ = ["FlashComponentSteps"]


class FlashComponentSteps(BaseComponentSteps):
    """Actions for the flash banner."""

    def __init__(self, driver: BaseDriver, base_url: str) -> None:
        super().__init__(driver, base_url)
        self.flash = FlashMessage(driver)

    def dismiss(self) -> Self:
        self.flash.close()
        return self

    @readonly
    def text(self) -> str:
        return self.flash.message()

    @readonly
    def wait_absent(self) -> Self:
        self.flash.wait_absent()
        return self
