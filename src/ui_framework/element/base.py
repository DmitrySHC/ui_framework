import copy
import time
from collections.abc import Callable
from contextlib import suppress
from typing import Literal, Protocol, Self

from playwright.sync_api import Error as PlaywrightError
from playwright.sync_api import Locator, Page
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError

from ..constants.driver import POLL_INTERVAL
from ..constants.element import DEFAULT_ELEMENT_WAIT, LOCATOR_FIELDS, LOCATOR_TEMPLATES, WAIT_TIMEOUT_MESSAGE
from ..driver.base import BaseDriver
from ..layers.scope import mutating
from .exceptions import ConditionNotMatchedException, ElementError

__all__ = ["BaseElement"]

LocatorState = Literal["attached", "detached", "hidden", "visible"]


class _Owner(Protocol):
    """Объект с ``driver``, на котором объявлен элемент."""

    @property
    def driver(self) -> BaseDriver: ...


class BaseElement:
    """Дескриптор элемента страницы: хранит один локатор и на каждое действие строит ``Locator`` заново.

    Принимает ровно один из ``css``, ``id``, ``xpath``, ``name``, ``class_name``, ``tag``;
    иначе ``ElementError``. ``label`` по умолчанию — имя атрибута класса.
    Методы ``wait_*`` ждут состояние до ``timeout`` секунд и поднимают
    ``ConditionNotMatchedException``.
    """

    def __init__(
        self,
        *,
        label: str | None = None,
        css: str | None = None,
        id: str | None = None,
        xpath: str | None = None,
        name: str | None = None,
        class_name: str | None = None,
        tag: str | None = None,
    ) -> None:
        candidates = {"css": css, "id": id, "xpath": xpath, "name": name, "class_name": class_name, "tag": tag}
        specified = {field: value for field, value in candidates.items() if value is not None}
        if len(specified) != 1:
            raise ElementError(f"exactly one locator from {LOCATOR_FIELDS} is required, got {sorted(specified)}")
        field, value = next(iter(specified.items()))
        self._locator_spec = (field, value)
        self._selector = LOCATOR_TEMPLATES[field].format(value)
        self.label = label
        self._owner: _Owner | None = None

    def __set_name__(self, owner: type, name: str) -> None:
        if self.label is None:
            self.label = name

    def __get__(self, obj: _Owner | None, objtype: type | None = None) -> Self:
        if obj is None:
            return self
        bound = copy.copy(self)
        bound._owner = obj
        return bound

    @property
    def locator(self) -> tuple[str, str]:
        return self._locator_spec

    @property
    def web_element(self) -> Locator:
        """``Locator`` Playwright для селектора элемента на текущей странице."""
        return self._locator()

    def _page(self) -> Page:
        if self._owner is None:
            raise ElementError(f"{self.label}: element is not bound to a page or component")
        return self._owner.driver.page

    def _locator(self) -> Locator:
        return self._page().locator(self._selector)

    def _timeout(self, what: str, seconds: float) -> ConditionNotMatchedException:
        return ConditionNotMatchedException(WAIT_TIMEOUT_MESSAGE.format(label=self.label, what=what, seconds=seconds))

    def _wait_for(self, state: LocatorState, timeout: float | None, what: str) -> None:
        seconds = DEFAULT_ELEMENT_WAIT if timeout is None else timeout
        try:
            self._locator().wait_for(state=state, timeout=int(seconds * 1000))
        except PlaywrightTimeoutError as error:
            raise self._timeout(what, seconds) from error

    def _wait_until(self, predicate: Callable[[], bool], timeout: float | None, what: str) -> None:
        seconds = DEFAULT_ELEMENT_WAIT if timeout is None else timeout
        deadline = time.monotonic() + seconds
        while time.monotonic() < deadline:
            # Пока элемент не стабилен, Playwright может бросить strict-mode или detached — пробуем дальше.
            with suppress(PlaywrightError):
                if predicate():
                    return
            time.sleep(POLL_INTERVAL)
        raise self._timeout(what, seconds)

    def wait_present(self, timeout: float | None = None) -> Self:
        self._wait_for("attached", timeout, "present")
        return self

    def wait_visible(self, timeout: float | None = None) -> Self:
        self._wait_for("visible", timeout, "visible")
        return self

    def wait_hidden(self, timeout: float | None = None) -> Self:
        self._wait_for("hidden", timeout, "hidden")
        return self

    def wait_absent(self, timeout: float | None = None) -> Self:
        self._wait_for("detached", timeout, "absent")
        return self

    def wait_clickable(self, timeout: float | None = None) -> Self:
        self._wait_until(lambda: self._locator().is_visible() and self._locator().is_enabled(), timeout, "clickable")
        return self

    def wait_enabled(self, timeout: float | None = None) -> Self:
        self._wait_until(lambda: self._locator().count() > 0 and self._locator().first.is_enabled(), timeout, "enabled")
        return self

    def wait_disabled(self, timeout: float | None = None) -> Self:
        self._wait_until(
            lambda: self._locator().count() > 0 and not self._locator().first.is_enabled(), timeout, "disabled"
        )
        return self

    @mutating
    def click(self, timeout: float | None = None) -> Self:
        self.wait_clickable(timeout=timeout)
        self._locator().click()
        return self

    @property
    def text(self) -> str:
        self.wait_present()
        return self._locator().inner_text()

    def get_attribute(self, name: str) -> str | None:
        self.wait_present()
        return self._locator().get_attribute(name)
