from .base import BaseElement

__all__ = ["Link"]


class Link(BaseElement):
    @property
    def href(self) -> str | None:
        return self.get_attribute("href")
