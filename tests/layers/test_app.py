import pytest

from ui_framework import BaseDriver, ChromeDriver, LayerError, StepsGroup

from .sample_layers import BASE, Asserts, SampleApp, Steps


class AppWithHelper(StepsGroup):
    def __init__(self, driver: BaseDriver, base_url: str) -> None:
        super().__init__(driver, base_url)
        self.steps = Steps(driver, base_url)
        self.asserts = Asserts(driver, base_url)
        self.timeout = 5


class AppWithoutAsserts(StepsGroup):
    def __init__(self, driver: BaseDriver, base_url: str) -> None:
        super().__init__(driver, base_url)
        self.steps = Steps(driver, base_url)


class NestedPlain(StepsGroup):
    def __init__(self, driver: BaseDriver, base_url: str) -> None:
        super().__init__(driver, base_url)
        self.timeout = 5


class OuterWithNestedPlain(StepsGroup):
    def __init__(self, driver: BaseDriver, base_url: str) -> None:
        super().__init__(driver, base_url)
        self.inner = NestedPlain(driver, base_url)


class GroupBuildingApp(StepsGroup):
    def __init__(self, driver: BaseDriver, base_url: str) -> None:
        super().__init__(driver, base_url)
        self.app = SampleApp(driver, base_url)


def test_app_exposes_steps_and_asserts(idle_driver: ChromeDriver) -> None:
    app = SampleApp(idle_driver, BASE)
    assert isinstance(app.steps, Steps)
    assert isinstance(app.asserts, Asserts)
    assert set(vars(app)) == {"steps", "asserts"}


def test_root_allows_extra_attribute(idle_driver: ChromeDriver) -> None:
    app = AppWithHelper(idle_driver, BASE)
    assert app.timeout == 5
    assert isinstance(app.steps, Steps)
    assert isinstance(app.asserts, Asserts)


def test_root_does_not_require_asserts(idle_driver: ChromeDriver) -> None:
    app = AppWithoutAsserts(idle_driver, BASE)
    assert isinstance(app.steps, Steps)
    assert not hasattr(app, "asserts")


def test_nested_group_rejects_plain_value(idle_driver: ChromeDriver) -> None:
    with pytest.raises(LayerError, match="may only hold"):
        OuterWithNestedPlain(idle_driver, BASE)


def test_nested_aggregator_cannot_hold_asserts(idle_driver: ChromeDriver) -> None:
    with pytest.raises(LayerError, match="root steps group"):
        GroupBuildingApp(idle_driver, BASE)


def test_app_drives_scenario(driver: ChromeDriver) -> None:
    app = SampleApp(driver, BASE)
    app.steps.widgets.open().type_username("alice")
    app.asserts.widgets.heading_is("Widgets").username_is("alice").status_is("Ready")
    app.steps.widgets.submit()
    app.asserts.widgets.status_is("Clicked")
