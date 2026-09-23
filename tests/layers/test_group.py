import pytest

from ui_framework import AssertsGroup, BaseDriver, ChromeDriver, LayerError, StepsGroup

from .sample_layers import BASE, Asserts, Steps, WidgetAsserts, WidgetSteps


class NestedSteps(StepsGroup):
    def __init__(self, driver: BaseDriver, base_url: str) -> None:
        super().__init__(driver, base_url)
        self.inner = Steps(driver, base_url)


class StepsWithAssert(StepsGroup):
    def __init__(self, driver: BaseDriver, base_url: str) -> None:
        super().__init__(driver, base_url)
        self.widgets = WidgetAsserts(driver, base_url)


class NestedWithAssert(StepsGroup):
    def __init__(self, driver: BaseDriver, base_url: str) -> None:
        super().__init__(driver, base_url)
        self.inner = StepsWithAssert(driver, base_url)


class AssertsWithValue(AssertsGroup):
    def __init__(self, driver: BaseDriver, base_url: str) -> None:
        super().__init__(driver, base_url)
        self.timeout = 5


def test_group_holds_steps(idle_driver: ChromeDriver):
    steps = Steps(idle_driver, BASE)
    assert isinstance(steps.widgets, WidgetSteps)


def test_group_holds_nested_groups(idle_driver: ChromeDriver):
    nested = NestedSteps(idle_driver, BASE)
    assert isinstance(nested.inner, Steps)
    assert isinstance(nested.inner.widgets, WidgetSteps)


def test_asserts_group_holds_asserts(idle_driver: ChromeDriver):
    asserts = Asserts(idle_driver, BASE)
    assert isinstance(asserts.widgets, WidgetAsserts)


def test_nested_steps_group_rejects_asserts(idle_driver: ChromeDriver):
    with pytest.raises(LayerError, match="root steps group"):
        NestedWithAssert(idle_driver, BASE)


def test_root_steps_group_holds_asserts(idle_driver: ChromeDriver):
    group = StepsWithAssert(idle_driver, BASE)
    assert isinstance(group.widgets, WidgetAsserts)


def test_asserts_group_rejects_plain_value(idle_driver: ChromeDriver):
    with pytest.raises(LayerError, match="may only hold"):
        AssertsWithValue(idle_driver, BASE)
