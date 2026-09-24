from typing import Self

from ui_framework import BaseComponent, Link, Text

__all__ = ["FlashMessage"]


class FlashMessage(BaseComponent):
    """The flash banner: its text and the close control."""

    banner = Text(id="flash")
    dismiss = Link(css="#flash a.close")

    def message(self) -> str:
        return self.banner.text.strip()

    def close(self) -> Self:
        self.dismiss.click()
        return self

    def wait_absent(self) -> Self:
        self.banner.wait_absent()
        return self
