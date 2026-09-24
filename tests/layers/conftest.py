from collections.abc import Iterator
from pathlib import Path

import pytest

from ui_framework import ChromeDriver, DriverConfig


@pytest.fixture
def idle_driver(tmp_path: Path) -> Iterator[ChromeDriver]:
    """A ChromeDriver that was never started. Logs go to tmp_path."""
    instance = ChromeDriver(DriverConfig(logs_dir=tmp_path))
    try:
        yield instance
    finally:
        instance.quit()
