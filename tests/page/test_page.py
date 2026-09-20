import pytest

from ui_framework import BasePage, PageError, url
from ui_framework.driver import ChromeDriver

_BASE = "https://example.com"


@url("/")
class HomePage(BasePage):
    pass


@url("/login")
class LoginPage(BasePage):
    pass


class UndecoratedPage(BasePage):
    pass


@url("/login/{user}")
class UserPage(BasePage):
    pass


def test_open_home(driver: ChromeDriver) -> None:
    page = HomePage(driver, _BASE)
    page.open()
    assert page.current_url.startswith(_BASE)
    assert page.title


def test_open_with_placeholder(driver: ChromeDriver) -> None:
    page = UserPage(driver, _BASE)
    page.open(user="alice")
    assert "login/alice" in page.current_url


def test_refresh_keeps_url(driver: ChromeDriver) -> None:
    page = LoginPage(driver, _BASE)
    page.open()
    before = page.current_url
    page.refresh()
    assert page.current_url == before


def test_undecorated_page_raises(driver: ChromeDriver) -> None:
    with pytest.raises(PageError, match="@url"):
        UndecoratedPage(driver, _BASE)


def test_wait_loaded_returns_self(driver: ChromeDriver) -> None:
    page = HomePage(driver, _BASE)
    assert page.wait_loaded() is page
