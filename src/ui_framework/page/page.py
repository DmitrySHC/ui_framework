from collections.abc import Callable
from typing import Any, ClassVar, Self, TypeVar
from urllib.parse import quote, urljoin

from ..constants.layers import Layer
from ..driver.base import BaseDriver
from ..layers.scope import ensure_mutable
from .exceptions import PageError
from .instance import BaseInstance

__all__ = ["BasePage", "url"]

PageT = TypeVar("PageT", bound="BasePage")


def url(path: str) -> Callable[[type[PageT]], type[PageT]]:
    """Sets the page path template. Placeholders look like {name}. Other classes raise PageError."""

    def decorator(cls: type[PageT]) -> type[PageT]:
        if not isinstance(cls, type) or not issubclass(cls, BasePage):
            name = getattr(cls, "__name__", type(cls).__name__)
            raise PageError(f"@url can only decorate a BasePage subclass, got {name}")
        cls.path = path
        return cls

    return decorator


class BasePage(BaseInstance):
    """A page with a path from the url decorator and a base URL.

    open navigates, refresh reloads. A class without the decorator raises PageError.
    """

    _layer: ClassVar[Layer | None] = "page"
    path: ClassVar[str | None] = None

    def __init__(self, driver: BaseDriver, base_url: str) -> None:
        template = type(self).path
        if template is None:
            raise PageError(f"{type(self).__name__} has no @url(...): set the page path")
        super().__init__(driver)
        self.base_url = base_url
        self._template = template

    def url(self, **kwargs: Any) -> str:
        """Absolute URL. Keyword arguments fill the path template and are quoted."""
        quoted = {name: quote(str(value), safe="") for name, value in kwargs.items()}
        return urljoin(f"{self.base_url.rstrip('/')}/", self._template.format(**quoted))

    def open(self, **kwargs: Any) -> Self:
        ensure_mutable(f"{type(self).__name__}.open")
        self.driver.open(self.url(**kwargs))
        return self.wait_loaded()

    def refresh(self) -> Self:
        ensure_mutable(f"{type(self).__name__}.refresh")
        self.driver.reload()
        return self.wait_loaded()

    def wait_loaded(self) -> Self:
        """Called after open and refresh. By default it waits for nothing and returns self."""
        return self

    @property
    def title(self) -> str:
        return self.driver.page.title()

    @property
    def current_url(self) -> str:
        return self.driver.page.url
