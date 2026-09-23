import pytest

from ui_framework import BaseDriver, BaseStep, ChromeDriver, LayerError

from .sample_layers import BASE, BrokenWidgetSteps, StatusBadge, WidgetsPage, WidgetSteps


class StepWithData(BaseStep):
    def __init__(self, driver: BaseDriver, base_url: str) -> None:
        super().__init__(driver, base_url)
        self.retries = 3


class StepBuildingPageLater(BaseStep):
    def another(self, driver: BaseDriver, base_url: str) -> WidgetsPage:
        return WidgetsPage(driver, base_url)


class StepBuildingComponent(BaseStep):
    def __init__(self, driver: BaseDriver, base_url: str) -> None:
        super().__init__(driver, base_url)
        self.badge = StatusBadge(driver)


def test_step_holds_pages_only(idle_driver: ChromeDriver):
    with pytest.raises(LayerError, match="may only hold page"):
        StepWithData(idle_driver, BASE)


def test_page_is_built_only_in_step_constructor(idle_driver: ChromeDriver):
    step = StepBuildingPageLater(idle_driver, BASE)
    with pytest.raises(LayerError, match="must be created in a step constructor"):
        step.another(idle_driver, BASE)


def test_component_is_not_built_in_step(idle_driver: ChromeDriver):
    with pytest.raises(LayerError, match="must be created in a page constructor"):
        StepBuildingComponent(idle_driver, BASE)


def test_step_cannot_touch_elements(idle_driver: ChromeDriver):
    with pytest.raises(LayerError, match="only page and component methods may use elements"):
        BrokenWidgetSteps(idle_driver, BASE).touch_element()


def test_step_cannot_reach_driver(idle_driver: ChromeDriver):
    with pytest.raises(LayerError, match=r"WidgetsPage\.driver"):
        BrokenWidgetSteps(idle_driver, BASE).touch_driver()


def test_top_level_page_keeps_driver_open(idle_driver: ChromeDriver):
    page = WidgetsPage(idle_driver, BASE)
    assert page.driver is idle_driver
    assert page.badge.driver is idle_driver


def test_assertion_in_step_is_layer_error(idle_driver: ChromeDriver):
    with pytest.raises(LayerError, match="AssertionError is only allowed in the asserts layer"):
        BrokenWidgetSteps(idle_driver, BASE).asserting()


def test_step_reads_state_through_pages(driver: ChromeDriver):
    steps = WidgetSteps(driver, BASE).open()
    assert steps.heading() == "Widgets"
    assert steps.status() == "Ready"
    assert steps.ready() is True
    steps.submit()
    assert steps.status() == "Clicked"
    assert steps.ready() is False
