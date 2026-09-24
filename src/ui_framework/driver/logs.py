import itertools
import logging
import os
from collections.abc import Iterable
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from ..constants.logs import (
    BROWSER_LOG_NAME,
    CONSOLE_LOG_LINE,
    CONSOLE_LOG_NAME,
    LOG_DIR_NAME_TEMPLATE,
    LOG_DIR_TIMESTAMP_FORMAT,
    SESSION_LOG_FORMAT,
    SESSION_LOG_NAME,
)

__all__ = ["ConsoleEntry", "DriverLogs"]

_counter = itertools.count(1)


@dataclass(frozen=True, slots=True)
class ConsoleEntry:
    """A console message or an uncaught page error."""

    level: str
    message: str


class DriverLogs:
    """Log directory for one run: browser.log, console.log, and session.log.

    The directory is created in the constructor.
    """

    def __init__(self, browser_name: str, logs_root: str | Path) -> None:
        self.directory = self._create_directory(browser_name, Path(logs_root))
        self.logger = self._configure_logger()

    @staticmethod
    def _create_directory(browser_name: str, logs_root: Path) -> Path:
        name = LOG_DIR_NAME_TEMPLATE.format(
            browser=browser_name,
            stamp=datetime.now().strftime(LOG_DIR_TIMESTAMP_FORMAT),
            pid=os.getpid(),
            # Avoid a name clash when two drivers start in the same second.
            index=next(_counter),
        )
        # Chrome starts with its own working directory, so the log path must be absolute.
        directory = logs_root.expanduser().resolve() / name
        directory.mkdir(parents=True, exist_ok=True)
        return directory

    def _configure_logger(self) -> logging.Logger:
        logger = logging.getLogger(f"{__name__}.{self.directory.name}")
        logger.setLevel(logging.DEBUG)
        logger.propagate = False
        handler = logging.FileHandler(self.session_log, encoding="utf-8")
        handler.setFormatter(logging.Formatter(SESSION_LOG_FORMAT))
        logger.addHandler(handler)
        return logger

    @property
    def browser_log(self) -> Path:
        return self.directory / BROWSER_LOG_NAME

    @property
    def console_log(self) -> Path:
        return self.directory / CONSOLE_LOG_NAME

    @property
    def session_log(self) -> Path:
        return self.directory / SESSION_LOG_NAME

    def append_console_entries(self, entries: Iterable[ConsoleEntry]) -> None:
        with self.console_log.open("a", encoding="utf-8") as stream:
            stream.writelines(CONSOLE_LOG_LINE.format(level=entry.level, message=entry.message) for entry in entries)

    def close(self) -> None:
        """Closes the log handlers. A second call does nothing."""
        for handler in list(self.logger.handlers):
            self.logger.removeHandler(handler)
            handler.close()

    def __repr__(self) -> str:
        return f"<DriverLogs {self.directory}>"
