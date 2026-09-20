from ui_framework.driver import ChromeDriver

from .sample_page import SamplePage

_BASE = "https://example.com"


def test_src_and_alt(driver: ChromeDriver) -> None:
    page = SamplePage(driver, _BASE)
    page.open()
    assert page.logo.alt == "Logo"
    assert page.logo.src is not None
    assert page.logo.src.startswith("data:image/")
