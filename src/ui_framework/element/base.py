import copy
import time
from collections.abc import Callable
from contextlib import suppress
from typing import Any, Literal, Protocol, Self, cast

from playwright.sync_api import Error as PlaywrightError
from playwright.sync_api import Locator, Page
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError

from ..constants.driver import POLL_INTERVAL
from ..constants.element import (
    DEFAULT_ELEMENT_WAIT,
    EXACT_LOCATORS,
    LOCATOR_FIELDS,
    LOCATOR_TEMPLATES,
    QUERY_LOCATORS,
    WAIT_TIMEOUT_MESSAGE,
)
from ..driver.base import BaseDriver
from ..layers.scope import mutating
from .exceptions import ConditionNotMatchedException, ElementError

__all__ = ["BaseElement"]

LocatorState = Literal["attached", "detached", "hidden", "visible"]


class _Owner(Protocol):
    """Owner that exposes a driver. The element is declared on it."""

    @property
    def driver(self) -> BaseDriver: ...


class BaseElement:
    """Finds one element and rebuilds the locator on every call.

    Pass one strategy: css, id, xpath, name, class_name, tag, role, by_label,
    placeholder, text, test_id, alt_text, or title. A widget with a fixed role,
    such as Button or Link, may be given only accessible_name. exact applies to
    role, label, text, placeholder, alt, and title. label defaults to the
    attribute name. A wait that runs out of time raises ConditionNotMatchedException.
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
        role: str | None = None,
        by_label: str | None = None,
        placeholder: str | None = None,
        text: str | None = None,
        test_id: str | None = None,
        alt_text: str | None = None,
        title: str | None = None,
        accessible_name: str | None = None,
        exact: bool = False,
    ) -> None:
        candidates = {
            "css": css,
            "id": id,
            "xpath": xpath,
            "name": name,
            "class_name": class_name,
            "tag": tag,
            "role": role,
            "label": by_label,
            "placeholder": placeholder,
            "text": text,
            "test_id": test_id,
            "alt_text": alt_text,
            "title": title,
        }
        specified = {field: value for field, value in candidates.items() if value is not None}
        if len(specified) > 1 or (len(specified) == 0 and accessible_name is None):
            fields = (*LOCATOR_FIELDS, *QUERY_LOCATORS)
            raise ElementError(f"exactly one locator from {fields} is required, got {sorted(specified)}")
        if len(specified) == 0:
            implied = getattr(type(self), "_role", None)
            if implied is None:
                raise ElementError(f"{type(self).__name__} has no role: pass role= or another locator")
            specified = {"role": implied}
        field, value = next(iter(specified.items()))
        if accessible_name is not None and field != "role":
            raise ElementError("accessible_name is only valid with role")
        if exact and field not in EXACT_LOCATORS:
            raise ElementError(f"exact is only valid with {sorted(EXACT_LOCATORS)}")
        self._locator_spec = (field, value)
        self._selector = "" if field in QUERY_LOCATORS else LOCATOR_TEMPLATES[field].format(value)
        self._accessible_name = accessible_name
        self._exact = exact
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
        """Playwright locator for this element on the current page."""
        return self._locator()

    def _page(self) -> Page:
        if self._owner is None:
            raise ElementError(f"{self.label}: element is not bound to a page or component")
        return self._owner.driver.page

    def _locator(self) -> Locator:
        root = self._page()
        field, value = self._locator_spec
        exact = {"exact": True} if self._exact else {}
        match field:
            case "role":
                return root.get_by_role(cast(Any, value), name=self._accessible_name, exact=self._exact)
            case "label":
                return root.get_by_label(value, **exact)
            case "placeholder":
                return root.get_by_placeholder(value, **exact)
            case "text":
                return root.get_by_text(value, **exact)
            case "test_id":
                return root.get_by_test_id(value)
            case "alt_text":
                return root.get_by_alt_text(value, **exact)
            case "title":
                return root.get_by_title(value, **exact)
            case _:
                return root.locator(self._selector)

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
            # The element may be detached or ambiguous for a moment. Keep polling.
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
