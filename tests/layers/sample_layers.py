from typing import Self

from ui_framework import (
    AssertsGroup,
    BaseAssert,
    BaseComponent,
    BaseComponentAsserts,
    BaseComponentSteps,
    BaseDriver,
    BasePage,
    BaseStep,
    Button,
    StepsGroup,
    Text,
    TextInput,
    readonly,
    url,
)

from ..element.sample_page import SAMPLE_HTML

BASE = "https://example.com"


class StatusBadge(BaseComponent):
    status = Text(id="status")

    def text(self) -> str:
        return self.status.text


@url(SAMPLE_HTML.as_uri())
class WidgetsPage(BasePage):
    heading = Text(id="heading")
    username = TextInput(id="username")
    submit = Button(id="submit")

    def __init__(self, driver: BaseDriver, base_url: str) -> None:
        super().__init__(driver, base_url)
        self.badge = StatusBadge(driver)

    def wait_loaded(self) -> Self:
        self.heading.wait_visible()
        return self

    def press_submit(self) -> Self:
        self.submit.click()
        return self

    def type_username(self, value: str) -> Self:
        self.username.fill(value)
        return self

    def heading_text(self) -> str:
        return self.heading.text

    def status_text(self) -> str:
        return self.badge.text()

    def username_value(self) -> str:
        return self.username.value

    @property
    def is_ready(self) -> bool:
        return self.badge.text() == "Ready"


class BadgeComponentSteps(BaseComponentSteps):
    def __init__(self, driver: BaseDriver, base_url: str) -> None:
        super().__init__(driver, base_url)
        self.badge = StatusBadge(driver)

    @readonly
    def text(self) -> str:
        return self.badge.text()

    def asserting(self) -> None:
        raise AssertionError("a component step must not assert")


class BadgeComponentAsserts(BaseComponentAsserts):
    def __init__(self, driver: BaseDriver, base_url: str) -> None:
        super().__init__(driver, base_url)
        self.step = BadgeComponentSteps(driver, base_url)

    def verify_text_is(self, text: str) -> Self:
        value = self.step.text()
        assert value == text, f"badge {value!r}, expected {text!r}"
        return self


class WidgetSteps(BaseStep):
    """Opens the widgets page, clicks, fills the field, and reads the page."""

    def __init__(self, driver: BaseDriver, base_url: str) -> None:
        super().__init__(driver, base_url)
        self.page = WidgetsPage(driver, base_url)
        self.badge = BadgeComponentSteps(driver, base_url)

    def open(self) -> Self:
        self.page.open()
        return self

    def refresh(self) -> Self:
        self.page.refresh()
        return self

    def submit(self) -> Self:
        self.page.press_submit()
        return self

    def type_username(self, value: str) -> Self:
        self.page.type_username(value)
        return self

    @readonly
    def status(self) -> str:
        return self.page.status_text()

    @readonly
    def heading(self) -> str:
        return self.page.heading_text()

    @readonly
    def username(self) -> str:
        return self.page.username_value()

    @readonly
    def ready(self) -> bool:
        return self.page.is_ready


class WidgetAsserts(BaseAssert):
    """Compares the heading, status, and field value with what the test expects."""

    def __init__(self, driver: BaseDriver, base_url: str) -> None:
        super().__init__(driver, base_url)
        self.step = WidgetSteps(driver, base_url)
        self.badge = BadgeComponentAsserts(driver, base_url)

    def verify_status_is(self, text: str) -> Self:
        status = self.step.status()
        assert status == text, f"status {status!r}, expected {text!r}"
        return self

    def verify_heading_is(self, text: str) -> Self:
        heading = self.step.heading()
        assert heading == text, f"heading {heading!r}, expected {text!r}"
        return self

    def verify_username_is(self, text: str) -> Self:
        value = self.step.username()
        assert value == text, f"field {value!r}, expected {text!r}"
        return self

    def verify_is_ready(self) -> Self:
        assert self.step.ready(), "page is not Ready"
        return self


class Steps(StepsGroup):
    def __init__(self, driver: BaseDriver, base_url: str) -> None:
        super().__init__(driver, base_url)
        self.widgets = WidgetSteps(driver, base_url)


class Asserts(AssertsGroup):
    def __init__(self, driver: BaseDriver, base_url: str) -> None:
        super().__init__(driver, base_url)
        self.widgets = WidgetAsserts(driver, base_url)


class SampleApp(StepsGroup):
    def __init__(self, driver: BaseDriver, base_url: str) -> None:
        super().__init__(driver, base_url)
        self.steps = Steps(driver, base_url)
        self.asserts = Asserts(driver, base_url)


class BrokenWidgetSteps(WidgetSteps):
    """Touches elements and the driver, mutates from a readonly method, and raises AssertionError."""

    def touch_element(self) -> str:
        return self.page.heading.text

    def touch_driver(self) -> str:
        return self.page.driver.page.url

    @readonly
    def sneaky_submit(self) -> Self:
        self.page.press_submit()
        return self

    @readonly
    def sneaky_refresh(self) -> Self:
        self.page.refresh()
        return self

    def asserting(self) -> None:
        raise AssertionError("a step must not assert")


class BrokenWidgetAsserts(BaseAssert):
    """A check that calls actions instead of reads."""

    def __init__(self, driver: BaseDriver, base_url: str) -> None:
        super().__init__(driver, base_url)
        self.step = BrokenWidgetSteps(driver, base_url)

    def tries_to_submit(self) -> Self:
        self.step.submit()
        return self

    def tries_sneaky_submit(self) -> Self:
        self.step.sneaky_submit()
        return self

    def tries_sneaky_refresh(self) -> Self:
        self.step.sneaky_refresh()
        return self
