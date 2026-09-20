import pytest

from ui_framework import BaseComponent, BasePage, PageError, url
from ui_framework.driver import ChromeDriver

_BASE = "https://example.com"


@url("/")
class HomePage(BasePage):
    def __init__(self, driver: ChromeDriver, base_url: str) -> None:
        super().__init__(driver, base_url)
        self.banner = SiteBanner(driver)


class SiteBanner(BaseComponent):
    pass


def test_composed_with_same_driver(driver: ChromeDriver) -> None:
    page = HomePage(driver, _BASE)
    assert page.banner.driver is driver
    assert page.driver is driver


def test_has_no_navigation(driver: ChromeDriver) -> None:
    banner = SiteBanner(driver)
    assert not hasattr(type(banner), "open")
    assert not hasattr(type(banner), "refresh")
    assert "url" not in type(banner).__dict__


def test_url_decorator_rejected() -> None:
    with pytest.raises(PageError, match="BasePage"):
        url("/")(SiteBanner)  # type: ignore[type-var]
