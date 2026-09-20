from collections.abc import Iterator, Mapping
from typing import Any

import pytest

from ..driver import ChromeDriver, DriverConfig

__all__ = ["driver", "webdriver_config", "webdriver_settings"]


@pytest.fixture
def webdriver_settings(request: pytest.FixtureRequest) -> Mapping[str, Any] | DriverConfig:
    """Поля ``DriverConfig`` или готовый конфиг; по умолчанию пустой dict.

    Значение берётся из ``request.param`` при ``parametrize(..., indirect=True)``.
    """
    return getattr(request, "param", {})


@pytest.fixture
def webdriver_config(webdriver_settings: Mapping[str, Any] | DriverConfig) -> DriverConfig:
    """Собирает ``DriverConfig`` из ``webdriver_settings``; готовый конфиг пропускает как есть."""
    if isinstance(webdriver_settings, DriverConfig):
        return webdriver_settings
    return DriverConfig(**dict(webdriver_settings))


@pytest.fixture
def driver(webdriver_config: DriverConfig) -> Iterator[ChromeDriver]:
    """Запущенный ``ChromeDriver``; после теста вызывает ``quit()``."""
    instance = ChromeDriver(webdriver_config)
    instance.start()
    try:
        yield instance
    finally:
        instance.quit()
