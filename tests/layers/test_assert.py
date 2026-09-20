import pytest

from ui_framework import BaseAssert, BaseDriver, ChromeDriver, LayerError

from .sample_layers import BASE, BrokenWidgetAsserts, SampleApp, WidgetsPage


class AssertWithPage(BaseAssert):
    def __init__(self, driver: BaseDriver, base_url: str) -> None:
        super().__init__(driver, base_url)
        self.page = WidgetsPage(driver, base_url)


class AssertWithData(BaseAssert):
    def __init__(self, driver: BaseDriver, base_url: str) -> None:
        super().__init__(driver, base_url)
        self.expected = "Ready"


def test_assert_holds_step_only(idle_driver: ChromeDriver) -> None:
    with pytest.raises(LayerError, match="may only hold step"):
        AssertWithData(idle_driver, BASE)


def test_assert_cannot_build_page(idle_driver: ChromeDriver) -> None:
    with pytest.raises(LayerError, match="must be created in a step constructor"):
        AssertWithPage(idle_driver, BASE)


def test_assert_cannot_call_step_action(idle_driver: ChromeDriver) -> None:
    with pytest.raises(LayerError, match="asserts layer is read-only"):
        BrokenWidgetAsserts(idle_driver, BASE).tries_to_submit()


def test_readonly_step_cannot_mutate_elements(idle_driver: ChromeDriver) -> None:
    with pytest.raises(LayerError, match=r"submit\.click: asserts layer is read-only"):
        BrokenWidgetAsserts(idle_driver, BASE).tries_sneaky_submit()


def test_readonly_step_cannot_navigate(idle_driver: ChromeDriver) -> None:
    with pytest.raises(LayerError, match=r"WidgetsPage\.refresh: asserts layer is read-only"):
        BrokenWidgetAsserts(idle_driver, BASE).tries_sneaky_refresh()


def test_assertion_error_is_raised_by_asserts(driver: ChromeDriver) -> None:
    app = SampleApp(driver, BASE)
    app.steps.widgets.open()
    app.asserts.widgets.status_is("Ready").is_ready()
    with pytest.raises(AssertionError, match="expected 'Clicked'"):
        app.asserts.widgets.status_is("Clicked")
