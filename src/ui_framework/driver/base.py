from abc import ABC, abstractmethod
from collections.abc import Mapping
from contextlib import suppress
from typing import Any, ClassVar, Self
from uuid import uuid4

from playwright.sync_api import Browser, BrowserContext, ConsoleMessage, Error, Page, Playwright, sync_playwright

from ..constants.driver import ENGINE_NAME, GOTO_WAIT
from .config import DriverConfig
from .exceptions import DriverConfigurationError, DriverNotStartedError
from .logs import ConsoleEntry, DriverLogs
from .network import NetworkInterceptor
from .profiles import DEVICE_PROFILES, DeviceProfile

__all__ = ["BaseDriver"]


class BaseDriver(ABC):
    """Сессия Playwright: браузер, контекст, страница и каталог логов.

    Конструктор принимает один аргумент — ``DriverConfig``. Наследник задаёт
    ``browser_name``, ``config_class`` и реализует ``_launch_browser``.
    """

    browser_name: ClassVar[str] = ""
    config_class: ClassVar[type[DriverConfig]] = DriverConfig

    def __new__(cls, *args: Any, **kwargs: Any) -> Self:
        if cls is BaseDriver:
            raise DriverConfigurationError("BaseDriver is abstract: use a subclass, for example ChromeDriver(...)")
        if not cls.browser_name:
            raise DriverConfigurationError(
                f"{cls.__name__} did not set browser_name: it is required for the log directory name"
            )
        cls._validate_constructor(args, kwargs)
        return super().__new__(cls)

    @classmethod
    def _validate_constructor(cls, args: tuple[Any, ...], kwargs: Mapping[str, Any]) -> None:
        if kwargs:
            raise DriverConfigurationError(
                f"{cls.__name__} takes only a config: {cls.__name__}({cls.config_class.__name__}(...))"
            )
        if len(args) != 1:
            raise DriverConfigurationError(
                f"{cls.__name__} takes one argument — {cls.config_class.__name__}(...); got {len(args)}"
            )
        config = args[0]
        if not isinstance(config, cls.config_class):
            raise DriverConfigurationError(
                f"{cls.__name__} takes {cls.config_class.__name__}, got {type(config).__name__}"
            )

    def __init__(self, config: DriverConfig) -> None:
        self.config = config
        self._playwright: Playwright | None = None
        self._browser: Browser | None = None
        self._context: BrowserContext | None = None
        self._page: Page | None = None
        self._session_id: str | None = None
        self._network: NetworkInterceptor | None = None
        self._console_entries: list[ConsoleEntry] = []
        self.logs = DriverLogs(self.browser_name, config.logs_dir)
        self._log = self.logs.logger
        self._log.info("driver config: %s", self.describe())

    @property
    def device_profile(self) -> DeviceProfile | None:
        device = self.config.device
        return None if device is None else DEVICE_PROFILES[device]

    def describe(self) -> dict[str, Any]:
        payload = self.config.model_dump(mode="json")
        payload["browser"] = self.browser_name
        payload["log_dir"] = str(self.logs.directory)
        payload["engine"] = ENGINE_NAME
        return payload

    def console_logs(self) -> list[ConsoleEntry]:
        """Сообщения консоли и JS-ошибки, накопленные с момента ``start()``."""
        return list(self._console_entries)

    @abstractmethod
    def _launch_browser(self, playwright: Playwright) -> Browser:
        """Запускает браузер по параметрам ``self.config``."""

    def start(self) -> Self:
        if self.is_started:
            self._log.debug("start() called again: session already running")
            return self

        self._log.info("starting %s", self.browser_name)
        self._playwright = sync_playwright().start()
        try:
            self._browser = self._launch_browser(self._playwright)
            self._context = self._browser.new_context(**self._context_options())
            self._page = self._context.new_page()
        except Exception as error:
            self._log.error("session failed (%s): %s", type(error).__name__, error)
            self._log.info("see %s", self.logs.browser_log)
            self._shutdown()
            raise

        self._session_id = uuid4().hex
        self._apply_timeouts()
        self._subscribe_console()
        self._log.info("session started: %s", self.session_id)
        return self

    def _context_options(self) -> dict[str, Any]:
        profile = self.device_profile
        if profile is None:
            width, height = self.config.window_size
            return {"viewport": {"width": width, "height": height}}
        return profile.context_options()

    def _apply_timeouts(self) -> None:
        self.page.set_default_navigation_timeout(int(self.config.page_load_timeout * 1000))
        self.page.set_default_timeout(int(self.config.script_timeout * 1000))

    def _subscribe_console(self) -> None:
        self.page.on("console", self._on_console)
        self.page.on("pageerror", self._on_page_error)

    def _on_console(self, message: ConsoleMessage) -> None:
        self._record(ConsoleEntry(level=message.type.upper(), message=message.text))

    def _on_page_error(self, error: Error) -> None:
        self._record(ConsoleEntry(level="ERROR", message=str(error)))

    def _record(self, entry: ConsoleEntry) -> None:
        self._console_entries.append(entry)
        try:
            self.logs.append_console_entries((entry,))
        except OSError as error:
            self._log.warning("failed to write console.log: %s", error)

    @property
    def is_started(self) -> bool:
        return self._page is not None

    @property
    def page(self) -> Page:
        if self._page is None:
            raise DriverNotStartedError(f"{type(self).__name__} is not started: call start() before using the session")
        return self._page

    @property
    def webdriver(self) -> Page:
        """То же, что ``page``."""
        return self.page

    @property
    def session_id(self) -> str | None:
        """Уникальный идентификатор текущей сессии; None до ``start()`` и после ``quit()``."""
        return self._session_id

    @property
    def network(self) -> NetworkInterceptor:
        if self._network is None:
            self._network = NetworkInterceptor(self)
        return self._network

    def open(self, url: str) -> Self:
        """Переходит по URL; чего ждать после навигации, задаёт ``page_load_strategy``."""
        self._log.info("opening %s", url)
        self.page.goto(url, wait_until=GOTO_WAIT[self.config.page_load_strategy])
        return self

    def reload(self) -> Self:
        """Перезагружает текущую страницу с тем же ожиданием, что и ``open()``."""
        self._log.info("reloading page")
        self.page.reload(wait_until=GOTO_WAIT[self.config.page_load_strategy])
        return self

    def _shutdown(self) -> None:
        """Закрывает браузер со всеми контекстами и страницами, останавливает Playwright, сбрасывает состояние."""
        browser, self._browser = self._browser, None
        playwright, self._playwright = self._playwright, None
        self._page = self._context = None
        self._session_id = self._network = None
        if browser is not None:
            with suppress(Exception):
                browser.close()
        if playwright is not None:
            with suppress(Exception):
                playwright.stop()

    def quit(self) -> None:
        """Закрывает браузер и файл session.log; повторный вызов ничего не делает."""
        was_started = self.is_started
        try:
            self._shutdown()
            if was_started:
                self._log.info("session closed")
        finally:
            self.logs.close()

    def __repr__(self) -> str:
        state = f"session={self.session_id}" if self.is_started else "not started"
        return f"<{type(self).__name__} {state} logs={self.logs.directory.name}>"
