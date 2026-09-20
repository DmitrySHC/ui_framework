from ui_framework.driver import ChromeDriver

from .sample_page import SamplePage

_BASE = "https://example.com"


def test_select_by_text_and_value(driver: ChromeDriver) -> None:
    page = SamplePage(driver, _BASE)
    page.open()
    page.country.select_by_text("USA")
    assert page.country.selected_text == "USA"
    page.country.select_by_value("ru")
    assert page.country.selected_text == "Russia"
