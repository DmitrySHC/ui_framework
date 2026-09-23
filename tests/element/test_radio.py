from ui_framework.driver import ChromeDriver

from .sample_page import SamplePage

_BASE = "https://example.com"


def test_select_radio(driver: ChromeDriver):
    page = SamplePage(driver, _BASE)
    page.open()
    assert page.color_red.is_selected is False
    page.color_red.select()
    assert page.color_red.is_selected is True
    page.color_blue.select()
    assert page.color_blue.is_selected is True
    assert page.color_red.is_selected is False
