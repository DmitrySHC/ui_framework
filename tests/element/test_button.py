from ui_framework.driver import ChromeDriver

from .sample_page import SamplePage

_BASE = "https://example.com"


def test_click(driver: ChromeDriver):
    page = SamplePage(driver, _BASE)
    page.open()
    page.submit.click()
    assert page.status.text == "Clicked"
