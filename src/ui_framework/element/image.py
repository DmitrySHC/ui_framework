from .base import BaseElement

__all__ = ["Image"]


class Image(BaseElement):
    _role = "img"
    @property
    def src(self) -> str | None:
        return self.get_attribute("src")

    @property
    def alt(self) -> str | None:
        return self.get_attribute("alt")
