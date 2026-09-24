import pytest

from ui_framework import (
    BaseAssert,
    BaseComponentAsserts,
    BaseDriver,
    ChromeDriver,
    ConditionNotMatchedException,
    LayerError,
)

from .sample_layers import (
    BASE,
    BadgeComponentAsserts,
    BadgeComponentSteps,
    BrokenWidgetAsserts,
    SampleApp,
    StatusBadge,
    WidgetAsserts,
    WidgetsPage,
)


class AssertWithPage(BaseAssert):
    def __init__(self, driver: BaseDriver, base_url: str) -> None:
        super().__init__(driver, base_url)
        self.page = WidgetsPage(driver, base_url)


class AssertWithData(BaseAssert):
    def __init__(self, driver: BaseDriver, base_url: str) -> None:
        super().__init__(driver, base_url)
        self.expected = "Ready"


class AssertWithComponent(BaseAssert):
    def __init__(self, driver: BaseDriver, base_url: str) -> None:
        super().__init__(driver, base_url)
        self.badge = StatusBadge(driver)


def test_assert_holds_step_only(idle_driver: ChromeDriver):
    with pytest.raises(LayerError, match="may only hold step or component_assert"):
        AssertWithData(idle_driver, BASE)


def test_assert_cannot_build_page(idle_driver: ChromeDriver):
    with pytest.raises(LayerError, match="must be created in a step constructor"):
        AssertWithPage(idle_driver, BASE)


def test_assert_cannot_build_component(idle_driver: ChromeDriver):
    with pytest.raises(LayerError, match="must be created in a component_step or page or step constructor"):
        AssertWithComponent(idle_driver, BASE)


def test_assert_holds_component_assert(idle_driver: ChromeDriver):
    asserts = WidgetAsserts(idle_driver, BASE)
    assert isinstance(asserts.badge, BadgeComponentAsserts)


def test_assert_cannot_call_step_action(idle_driver: ChromeDriver):
    with pytest.raises(LayerError, match="asserts layer is read-only"):
        BrokenWidgetAsserts(idle_driver, BASE).tries_to_submit()


def test_readonly_step_cannot_mutate_elements(idle_driver: ChromeDriver):
    with pytest.raises(LayerError, match=r"submit\.click: asserts layer is read-only"):
        BrokenWidgetAsserts(idle_driver, BASE).tries_sneaky_submit()


def test_readonly_step_cannot_navigate(idle_driver: ChromeDriver):
    with pytest.raises(LayerError, match=r"WidgetsPage\.refresh: asserts layer is read-only"):
        BrokenWidgetAsserts(idle_driver, BASE).tries_sneaky_refresh()


def test_assertion_error_is_raised_by_asserts(driver: ChromeDriver):
    app = SampleApp(driver, BASE)
    app.steps.widgets.open()
    app.asserts.widgets.verify_status_is("Ready").verify_is_ready()
    with pytest.raises(AssertionError, match="expected 'Clicked'"):
        app.asserts.widgets.verify_status_is("Clicked")


def test_component_assert_reads_component_step(driver: ChromeDriver):
    app = SampleApp(driver, BASE)
    app.steps.widgets.open()
    app.asserts.widgets.badge.verify_text_is("Ready")


class ActingSteps(BadgeComponentSteps):
    def poke(self) -> None:
        return None


class AssertThatActs(BaseComponentAsserts):
    def __init__(self, driver: BaseDriver, base_url: str) -> None:
        super().__init__(driver, base_url)
        self.step = ActingSteps(driver, base_url)

    def verify_pokes(self) -> None:
        self.step.poke()


def test_component_assert_cannot_call_action(idle_driver: ChromeDriver):
    with pytest.raises(LayerError, match="asserts layer is read-only"):
        AssertThatActs(idle_driver, BASE).verify_pokes()


def test_check_turns_timeout_into_assertion_error(idle_driver: ChromeDriver):
    def missed() -> None:
        raise ConditionNotMatchedException("banner: timed out waiting for absent after 10s")

    with pytest.raises(AssertionError, match="timed out waiting for absent") as info:
        BadgeComponentAsserts(idle_driver, BASE).check(missed)
    assert isinstance(info.value.__cause__, ConditionNotMatchedException)


def test_component_assert_keeps_assertion_error(driver: ChromeDriver):
    app = SampleApp(driver, BASE)
    app.steps.widgets.open()
    with pytest.raises(AssertionError, match="expected 'Clicked'"):
        app.asserts.widgets.badge.verify_text_is("Clicked")
