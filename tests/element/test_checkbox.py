from ui_framework.driver import ChromeDriver

from .sample_page import SamplePage

_BASE = "https://example.com"


def test_check_uncheck(driver: ChromeDriver):
    page = SamplePage(driver, _BASE)
    page.open()
    assert page.agree.is_checked is False
    page.agree.check()
    assert page.agree.is_checked is True
    page.agree.uncheck()
    assert page.agree.is_checked is False
