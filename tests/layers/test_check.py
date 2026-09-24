from pathlib import Path
from textwrap import dedent

import pytest

from ui_framework import element
from ui_framework.constants.layers import WIDGET_NAMES
from ui_framework.layers import ArchitectureError, check_project, ensure_architecture

DEMO_ROOT = Path(__file__).resolve().parents[2] / "demo"

STEP_MODULE = """
from ui_framework import BaseStep

from pages.widgets import WidgetsPage


class WidgetSteps(BaseStep):
    def __init__(self, driver, base_url):
        super().__init__(driver, base_url)
        self.page = WidgetsPage(driver, base_url)
"""

PAGE_MODULE = """
from ui_framework import BasePage, Text, url


@url("/widgets")
class WidgetsPage(BasePage):
    heading = Text(id="heading")
"""


def _write(root: Path, relative: str, source: str) -> None:
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(dedent(source).lstrip(), encoding="utf-8")


def _project(root: Path) -> Path:
    _write(root, "pages/widgets.py", PAGE_MODULE)
    _write(root, "steps/widgets.py", STEP_MODULE)
    return root


def _rules(root: Path) -> set[str]:
    return {violation.rule for violation in check_project(root)}


def test_widget_names_match_element_exports():
    exceptions = {"ConditionNotMatchedException", "ElementError"}
    assert set(element.__all__) - exceptions == set(WIDGET_NAMES)


def test_demo_project_is_clean():
    # Дублирует demo/tests/test_architecture.py намеренно: фреймворк проверяет чекер на живом проекте.
    assert check_project(DEMO_ROOT) == []


def test_clean_project_has_no_violations(tmp_path: Path):
    assert check_project(_project(tmp_path)) == []


def test_assert_outside_asserts(tmp_path: Path):
    _project(tmp_path)
    _write(
        tmp_path,
        "steps/checks.py",
        """
        def verify(value):
            assert value
        """,
    )
    assert _rules(tmp_path) == {"assert"}


def test_assertion_error_outside_asserts(tmp_path: Path):
    _project(tmp_path)
    _write(
        tmp_path,
        "tests/test_x.py",
        """
        def test_x():
            raise AssertionError("no")
        """,
    )
    assert _rules(tmp_path) == {"assert"}


def test_widgets_outside_pages(tmp_path: Path):
    _project(tmp_path)
    _write(tmp_path, "steps/extra.py", "from ui_framework import Button\n")
    assert _rules(tmp_path) == {"widgets"}


def test_element_module_outside_pages(tmp_path: Path):
    _project(tmp_path)
    _write(tmp_path, "steps/extra.py", "import ui_framework.element as widgets\n")
    assert _rules(tmp_path) == {"widgets"}


def test_layer_class_in_wrong_directory(tmp_path: Path):
    _project(tmp_path)
    _write(
        tmp_path,
        "steps/misplaced.py",
        """
        from ui_framework import BasePage, url


        @url("/misplaced")
        class MisplacedPage(BasePage):
            pass
        """,
    )
    assert _rules(tmp_path) == {"placement"}


def test_root_aggregator_is_allowed(tmp_path: Path):
    _project(tmp_path)
    _write(
        tmp_path,
        "app.py",
        """
        from ui_framework import StepsGroup


        class App(StepsGroup):
            pass
        """,
    )
    assert check_project(tmp_path) == []


def test_root_aggregator_may_construct_asserts(tmp_path: Path):
    _project(tmp_path)
    _write(
        tmp_path,
        "asserts/bundle.py",
        """
        from ui_framework import AssertsGroup


        class Asserts(AssertsGroup):
            pass
        """,
    )
    _write(
        tmp_path,
        "steps/bundle.py",
        """
        from ui_framework import StepsGroup


        class Steps(StepsGroup):
            pass
        """,
    )
    _write(
        tmp_path,
        "app.py",
        """
        from ui_framework import StepsGroup

        from asserts.bundle import Asserts
        from steps.bundle import Steps


        class App(StepsGroup):
            def __init__(self, driver, base_url):
                super().__init__(driver, base_url)
                self.steps = Steps(driver, base_url)
                self.asserts = Asserts(driver, base_url)
                self.timeout = 5
        """,
    )
    _write(
        tmp_path,
        "conftest.py",
        """
        from app import App


        def app(driver):
            return App(driver, "https://example.com")
        """,
    )
    _write(
        tmp_path,
        "tests/test_x.py",
        """
        from app import App


        def test_x(driver):
            App(driver, "https://example.com")
        """,
    )
    assert check_project(tmp_path) == []


def test_root_aggregator_outside_root(tmp_path: Path):
    _project(tmp_path)
    _write(
        tmp_path,
        "pages/app.py",
        """
        from ui_framework import StepsGroup


        class App(StepsGroup):
            pass
        """,
    )
    assert _rules(tmp_path) == {"placement"}


def test_page_built_outside_step_constructor(tmp_path: Path):
    _project(tmp_path)
    _write(
        tmp_path,
        "steps/later.py",
        """
        from ui_framework import BaseStep

        from pages.widgets import WidgetsPage


        class LaterSteps(BaseStep):
            def open_widgets(self, driver, base_url):
                return WidgetsPage(driver, base_url)
        """,
    )
    assert _rules(tmp_path) == {"construction"}


def test_component_built_in_step_constructor(tmp_path: Path):
    _project(tmp_path)
    _write(
        tmp_path,
        "pages/badge.py",
        """
        from ui_framework import BaseComponent, Text


        class StatusBadge(BaseComponent):
            status = Text(id="status")
        """,
    )
    _write(
        tmp_path,
        "steps/badge.py",
        """
        from ui_framework import BaseStep

        from pages.badge import StatusBadge


        class BadgeSteps(BaseStep):
            def __init__(self, driver, base_url):
                super().__init__(driver, base_url)
                self.badge = StatusBadge(driver)
        """,
    )
    assert _rules(tmp_path) == set()


def test_component_built_outside_page_or_step_constructor(tmp_path: Path):
    _project(tmp_path)
    _write(
        tmp_path,
        "pages/badge.py",
        """
        from ui_framework import BaseComponent, Text


        class StatusBadge(BaseComponent):
            status = Text(id="status")
        """,
    )
    _write(
        tmp_path,
        "steps/later.py",
        """
        from ui_framework import BaseStep

        from pages.badge import StatusBadge


        class LaterSteps(BaseStep):
            def make_badge(self, driver):
                return StatusBadge(driver)
        """,
    )
    assert _rules(tmp_path) == {"construction"}


def test_component_step_built_in_step_constructor(tmp_path: Path):
    _project(tmp_path)
    _write(
        tmp_path,
        "pages/badge.py",
        """
        from ui_framework import BaseComponent, Text


        class StatusBadge(BaseComponent):
            status = Text(id="status")
        """,
    )
    _write(
        tmp_path,
        "steps/badge.py",
        """
        from ui_framework import BaseComponentSteps, BaseStep

        from pages.badge import StatusBadge


        class BadgeSteps(BaseComponentSteps):
            def __init__(self, driver, base_url):
                super().__init__(driver, base_url)
                self.badge = StatusBadge(driver)


        class HostSteps(BaseStep):
            def __init__(self, driver, base_url):
                super().__init__(driver, base_url)
                self.badge = BadgeSteps(driver, base_url)
        """,
    )
    assert _rules(tmp_path) == set()


def test_component_step_built_outside_constructor(tmp_path: Path):
    _project(tmp_path)
    _write(
        tmp_path,
        "steps/later.py",
        """
        from ui_framework import BaseComponentSteps, BaseStep


        class BadgeSteps(BaseComponentSteps):
            pass


        class LaterSteps(BaseStep):
            def make_badge(self, driver, base_url):
                return BadgeSteps(driver, base_url)
        """,
    )
    assert _rules(tmp_path) == {"construction"}


def test_driver_access_outside_pages(tmp_path: Path):
    _project(tmp_path)
    _write(
        tmp_path,
        "steps/raw.py",
        """
        from ui_framework import BaseStep


        class RawSteps(BaseStep):
            def url(self):
                return self.page.driver.page.url
        """,
    )
    assert _rules(tmp_path) == {"driver"}


def test_tests_use_only_entry_point(tmp_path: Path):
    _project(tmp_path)
    _write(
        tmp_path,
        "tests/test_direct.py",
        """
        from steps.widgets import WidgetSteps


        def test_direct(driver):
            WidgetSteps(driver, "https://example.com")
        """,
    )
    assert _rules(tmp_path) == {"tests", "construction"}


def test_ensure_architecture_lists_violations(tmp_path: Path):
    _project(tmp_path)
    _write(tmp_path, "steps/extra.py", "from ui_framework import Button\n")
    with pytest.raises(ArchitectureError, match=r"layer violations \(1\)") as info:
        ensure_architecture(tmp_path)
    assert "steps" in str(info.value)
    assert "[widgets]" in str(info.value)
