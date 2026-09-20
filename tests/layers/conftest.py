from collections.abc import Iterator
from pathlib import Path

import pytest

from ui_framework import ChromeDriver, DriverConfig


@pytest.fixture
def idle_driver(tmp_path: Path) -> Iterator[ChromeDriver]:
    """``ChromeDriver`` без ``start()``: браузер не запускается, логи пишутся в ``tmp_path``."""
    instance = ChromeDriver(DriverConfig(logs_dir=tmp_path))
    try:
        yield instance
    finally:
        instance.quit()
