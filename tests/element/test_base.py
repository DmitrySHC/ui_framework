import pytest

from ui_framework import BaseElement, ConditionNotMatchedException, ElementError
from ui_framework.driver import ChromeDriver

from .sample_page import SamplePage

_BASE = "https://example.com"
_SHORT = 0.4


def test_exactly_one_locator_required() -> None:
    with pytest.raises(ElementError, match="exactly one locator"):
        BaseElement()
    with pytest.raises(ElementError, match="exactly one locator"):
        BaseElement(css="#a", id="b")


def test_label_defaults_to_attribute_name() -> None:
    assert SamplePage.heading.label == "heading"
    assert SamplePage.missing.label == "Missing"


def test_wait_visible_and_text(driver: ChromeDriver) -> None:
    page = SamplePage(driver, _BASE)
    page.open()
    page.heading.wait_visible()
    assert page.heading.text == "Widgets"


def test_wait_present(driver: ChromeDriver) -> None:
    page = SamplePage(driver, _BASE)
    page.open()
    page.secret.wait_present()
    assert page.secret.get_attribute("id") == "secret"


def test_wait_hidden(driver: ChromeDriver) -> None:
    page = SamplePage(driver, _BASE)
    page.open()
    page.secret.wait_hidden(_SHORT)


def test_wait_absent(driver: ChromeDriver) -> None:
    page = SamplePage(driver, _BASE)
    page.open()
    page.missing.wait_absent(_SHORT)


def test_wait_enabled_and_disabled(driver: ChromeDriver) -> None:
    page = SamplePage(driver, _BASE)
    page.open()
    page.submit.wait_enabled()
    page.frozen.wait_disabled()


def test_wait_clickable_then_click(driver: ChromeDriver) -> None:
    page = SamplePage(driver, _BASE)
    page.open()
    page.submit.wait_clickable().click()
    assert page.status.text == "Clicked"


def test_wait_visible_times_out(driver: ChromeDriver) -> None:
    page = SamplePage(driver, _BASE)
    page.open()
    with pytest.raises(ConditionNotMatchedException, match="Missing"):
        page.missing.wait_visible(timeout=_SHORT)
