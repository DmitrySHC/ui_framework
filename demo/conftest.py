import pytest

from ui_framework import BaseDriver

from demo.app import BASE_URL, TheInternet

pytest_plugins = ("ui_framework.fixtures.driver",)


@pytest.fixture
def webdriver_settings() -> dict[str, object]:
    return {"window_size": (1280, 800)}


@pytest.fixture
def app(driver: BaseDriver) -> TheInternet:
    return TheInternet(driver, BASE_URL)
