from .base import BaseElement

__all__ = ["Link"]


class Link(BaseElement):
    _role = "link"
    @property
    def href(self) -> str | None:
        return self.get_attribute("href")
