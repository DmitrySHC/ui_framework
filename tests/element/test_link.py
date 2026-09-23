from ui_framework.driver import ChromeDriver

from .sample_page import SamplePage

_BASE = "https://example.com"


def test_href(driver: ChromeDriver):
    page = SamplePage(driver, _BASE)
    page.open()
    assert page.docs.href is not None
    assert page.docs.href.endswith("/docs")
    assert page.docs.text == "Docs"
