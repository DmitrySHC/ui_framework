import pytest

from ui_framework import BaseElement, Button, ConditionNotMatchedException, ElementError, Text, TextInput, url
from ui_framework.driver import ChromeDriver

from .sample_page import SAMPLE_HTML, SamplePage

_BASE = "https://example.com"
_SHORT = 0.4


def test_exactly_one_locator_required():
    with pytest.raises(ElementError, match="exactly one locator"):
        BaseElement()
    with pytest.raises(ElementError, match="exactly one locator"):
        BaseElement(css="#a", id="b")
    with pytest.raises(ElementError, match="accessible_name is only valid with role"):
        BaseElement(css="#a", accessible_name="Go")
    with pytest.raises(ElementError, match="exact is only valid"):
        BaseElement(css="#a", exact=True)
    with pytest.raises(ElementError, match="has no role"):
        Text(accessible_name="Widgets")


@url(SAMPLE_HTML.as_uri())
class AccessiblePage(SamplePage):
    go = Button(accessible_name="Go")
    user = TextInput(by_label="User")
    heading_role = Text(role="heading", accessible_name="Widgets")


def test_label_defaults_to_attribute_name():
    assert SamplePage.heading.label == "heading"
    assert SamplePage.missing.label == "Missing"


def test_wait_visible_and_text(driver: ChromeDriver):
    page = SamplePage(driver, _BASE)
    page.open()
    page.heading.wait_visible()
    assert page.heading.text == "Widgets"


def test_wait_present(driver: ChromeDriver):
    page = SamplePage(driver, _BASE)
    page.open()
    page.secret.wait_present()
    assert page.secret.get_attribute("id") == "secret"


def test_wait_hidden(driver: ChromeDriver):
    page = SamplePage(driver, _BASE)
    page.open()
    page.secret.wait_hidden(_SHORT)


def test_wait_absent(driver: ChromeDriver):
    page = SamplePage(driver, _BASE)
    page.open()
    page.missing.wait_absent(_SHORT)


def test_wait_enabled_and_disabled(driver: ChromeDriver):
    page = SamplePage(driver, _BASE)
    page.open()
    page.submit.wait_enabled()
    page.frozen.wait_disabled()


def test_wait_clickable_then_click(driver: ChromeDriver):
    page = SamplePage(driver, _BASE)
    page.open()
    page.submit.wait_clickable().click()
    assert page.status.text == "Clicked"


def test_role_and_label_locators(driver: ChromeDriver):
    page = AccessiblePage(driver, _BASE)
    page.open()
    assert page.go.text.strip() == "Go"
    assert page.user.locator == ("label", "User")
    assert page.heading_role.text == "Widgets"
    page.go.click()
    assert page.status.text == "Clicked"


def test_wait_visible_times_out(driver: ChromeDriver):
    page = SamplePage(driver, _BASE)
    page.open()
    with pytest.raises(ConditionNotMatchedException, match="Missing"):
        page.missing.wait_visible(timeout=_SHORT)
