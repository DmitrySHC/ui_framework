from typing import Self

from ui_framework import BaseComponentAsserts, BaseDriver

from demo.steps.components.flash import FlashComponentSteps

__all__ = ["FlashComponentAsserts"]


class FlashComponentAsserts(BaseComponentAsserts):
    def __init__(self, driver: BaseDriver, base_url: str) -> None:
        super().__init__(driver, base_url)
        self.step = FlashComponentSteps(driver, base_url)

    def contains(self, text: str) -> Self:
        flash = self.step.text()
        assert text.lower() in flash.lower(), f"{text!r} not in flash {flash!r}"
        return self

    def is_absent(self) -> Self:
        self.step.wait_absent()
        return self
