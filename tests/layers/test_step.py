import pytest

from ui_framework import BaseComponentSteps, BaseDriver, BaseStep, ChromeDriver, LayerError

from .sample_layers import (
    BASE,
    BadgeComponentSteps,
    BrokenWidgetSteps,
    StatusBadge,
    WidgetsPage,
    WidgetSteps,
)


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

    def status(self) -> str:
        return self.badge.text()


class StepBuildingComponentLater(BaseStep):
    def later(self, driver: BaseDriver) -> StatusBadge:
        return StatusBadge(driver)


class ComponentStepWithData(BaseComponentSteps):
    def __init__(self, driver: BaseDriver, base_url: str) -> None:
        super().__init__(driver, base_url)
        self.retries = 3


class ComponentStepBuildingLater(BaseComponentSteps):
    def later(self, driver: BaseDriver, base_url: str) -> BadgeComponentSteps:
        return BadgeComponentSteps(driver, base_url)


def test_step_holds_pages_or_components_only(idle_driver: ChromeDriver):
    with pytest.raises(LayerError, match="may only hold page or component or component_step"):
        StepWithData(idle_driver, BASE)


def test_page_is_built_only_in_step_constructor(idle_driver: ChromeDriver):
    step = StepBuildingPageLater(idle_driver, BASE)
    with pytest.raises(LayerError, match="must be created in a step constructor"):
        step.another(idle_driver, BASE)


def test_step_holds_component(idle_driver: ChromeDriver):
    step = StepBuildingComponent(idle_driver, BASE)
    assert isinstance(step.badge, StatusBadge)


def test_component_is_built_only_in_page_or_step_constructor(idle_driver: ChromeDriver):
    step = StepBuildingComponentLater(idle_driver, BASE)
    with pytest.raises(LayerError, match="must be created in a component_step or page or step constructor"):
        step.later(idle_driver)


def test_step_holds_component_step(idle_driver: ChromeDriver):
    step = WidgetSteps(idle_driver, BASE)
    assert isinstance(step.badge, BadgeComponentSteps)


def test_component_step_holds_component_only(idle_driver: ChromeDriver):
    with pytest.raises(LayerError, match="may only hold component"):
        ComponentStepWithData(idle_driver, BASE)


def test_component_step_is_built_only_in_allowed_constructor(idle_driver: ChromeDriver):
    step = ComponentStepBuildingLater(idle_driver, BASE)
    with pytest.raises(LayerError, match="must be created in a component_assert or step or steps constructor"):
        step.later(idle_driver, BASE)


def test_assertion_in_component_step_is_layer_error(idle_driver: ChromeDriver):
    with pytest.raises(LayerError, match="AssertionError is only allowed in the asserts layer"):
        BadgeComponentSteps(idle_driver, BASE).asserting()


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


def test_step_reads_component_it_holds(driver: ChromeDriver):
    WidgetsPage(driver, BASE).open()
    assert StepBuildingComponent(driver, BASE).status() == "Ready"
