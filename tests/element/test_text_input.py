from ui_framework.driver import ChromeDriver

from .sample_page import SamplePage

_BASE = "https://example.com"


def test_fill_clear_value(driver: ChromeDriver):
    page = SamplePage(driver, _BASE)
    page.open()
    page.username.fill("alice")
    assert page.username.value == "alice"
    page.username.clear()
    assert page.username.value == ""
