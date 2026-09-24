import time
from collections.abc import Callable, Iterator
from contextlib import contextmanager, suppress
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from playwright.sync_api import Route

from ..constants.driver import POLL_INTERVAL
from ..constants.network import (
    ALL_URLS,
    CONTENT_TYPE_HEADER,
    DEFAULT_NETWORK_WAIT,
    DEFAULT_STUB_CONTENT_TYPE,
    DEFAULT_STUB_STATUS,
)
from .exceptions import NetworkError

if TYPE_CHECKING:
    from .base import BaseDriver

__all__ = ["NetworkInterceptor", "NetworkLog", "RequestRecord"]


@dataclass(frozen=True, slots=True)
class RequestRecord:
    method: str
    url: str
    headers: dict[str, str] = field(default_factory=dict)


@dataclass(slots=True)
class NetworkLog:
    """Requests captured by the current intercept."""

    requests: list[RequestRecord] = field(default_factory=list)

    def urls(self) -> list[str]:
        return [item.url for item in self.requests]

    def find(self, substring: str) -> RequestRecord | None:
        return next((item for item in self.requests if substring in item.url), None)

    def wait_for(self, substring: str, timeout: float = DEFAULT_NETWORK_WAIT) -> RequestRecord:
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            found = self.find(substring)
            if found is not None:
                return found
            time.sleep(POLL_INTERVAL)
        raise NetworkError(
            f"timed out waiting for a request containing {substring!r} after {timeout}s: {self.urls()[-10:]}"
        )


class NetworkInterceptor:
    """Routes page requests for the duration of a with block, then removes the route."""

    def __init__(self, driver: "BaseDriver") -> None:
        self._driver = driver

    @contextmanager
    def _on_route(self, patterns: tuple[str, ...], callback: Callable[[Route], None]) -> Iterator[None]:
        page = self._driver.page
        errors: list[Exception] = []
        globs = patterns or (ALL_URLS,)

        def wrapped(route: Route) -> None:
            try:
                callback(route)
            except Exception as error:  # noqa: BLE001 - колбэк не должен повесить страницу: пропускаем запрос, жалуемся после with
                errors.append(error)
                with suppress(Exception):
                    route.continue_()

        for glob in globs:
            page.route(glob, wrapped)
        try:
            yield
        finally:
            for glob in globs:
                with suppress(Exception):
                    page.unroute(glob, wrapped)
            if errors:
                raise errors[0]

    @contextmanager
    def intercept(self, *patterns: str) -> Iterator[NetworkLog]:
        """Records matching requests and lets them continue."""
        log = NetworkLog()

        def capture(route: Route) -> None:
            request = route.request
            log.requests.append(RequestRecord(method=request.method, url=request.url, headers=dict(request.headers)))
            route.continue_()

        with self._on_route(patterns, capture):
            yield log

    @contextmanager
    def stub(
        self,
        *patterns: str,
        status: int = DEFAULT_STUB_STATUS,
        body: str = "",
        headers: dict[str, str] | None = None,
        content_type: str = DEFAULT_STUB_CONTENT_TYPE,
    ) -> Iterator[None]:
        """Fulfills matching requests with a stub response."""
        merged = {CONTENT_TYPE_HEADER: content_type, **(headers or {})}

        def respond(route: Route) -> None:
            route.fulfill(status=status, headers=merged, body=body)

        with self._on_route(patterns, respond):
            yield

    @contextmanager
    def rewrite(self, *patterns: str, to: str) -> Iterator[None]:
        """Serves the response from another URL under the original address."""

        def mutate(route: Route) -> None:
            route.fulfill(response=route.fetch(url=to))

        with self._on_route(patterns, mutate):
            yield
