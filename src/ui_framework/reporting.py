from pathlib import Path

import allure

from .driver.base import BaseDriver

__all__ = ["attach_failure"]

_TEXT = allure.attachment_type.TEXT
_PNG = allure.attachment_type.PNG


def attach_failure(driver: BaseDriver) -> None:
    """Attaches the failure screenshot, logs, and trace to the current Allure test."""
    for handler in driver.logs.logger.handlers:
        handler.flush()
    directory = driver.logs.directory
    _file(directory / "failure.png", "Screenshot", _PNG)
    _file(driver.logs.session_log, "Session log", _TEXT)
    _file(driver.logs.console_log, "Console log", _TEXT)
    _file(directory / "trace.zip", "Playwright trace", None, extension="zip")


def _file(path: Path, name: str, attachment_type: allure.attachment_type | None, extension: str | None = None) -> None:
    if not path.is_file() or path.stat().st_size == 0:
        return
    allure.attach.file(str(path), name=name, attachment_type=attachment_type, extension=extension)  # type: ignore[no-untyped-call]
