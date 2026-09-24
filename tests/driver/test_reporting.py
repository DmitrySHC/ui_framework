from pathlib import Path
from types import SimpleNamespace
from typing import cast

import allure

from ui_framework import BaseDriver
from ui_framework.reporting import attach_failure


def test_failure_artifacts_are_attached(tmp_path: Path, monkeypatch):
    directory = tmp_path / "logs"
    directory.mkdir()
    (directory / "failure.png").write_bytes(b"png")
    (directory / "session.log").write_text("opened", encoding="utf-8")
    (directory / "console.log").write_text("error", encoding="utf-8")
    (directory / "trace.zip").write_bytes(b"zip")
    attached: list[str] = []

    def capture(source: str, name: str, attachment_type: object = None, extension: str | None = None) -> None:
        attached.append(name)

    monkeypatch.setattr(allure, "attach", SimpleNamespace(file=capture))
    logger = SimpleNamespace(handlers=[])
    driver = SimpleNamespace(
        logs=SimpleNamespace(
            logger=logger,
            directory=directory,
            session_log=directory / "session.log",
            console_log=directory / "console.log",
        )
    )
    attach_failure(cast(BaseDriver, driver))
    assert attached == ["Screenshot", "Session log", "Console log", "Playwright trace"]
