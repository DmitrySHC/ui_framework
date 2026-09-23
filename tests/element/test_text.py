from ui_framework.driver import ChromeDriver

from .sample_page import SamplePage

_BASE = "https://example.com"


def test_text_content(driver: ChromeDriver):
    page = SamplePage(driver, _BASE)
    page.open()
    assert page.status.text == "Ready"
    assert page.heading.text == "Widgets"
