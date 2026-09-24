import inspect
import sys
from collections.abc import Iterator, Mapping
from typing import Any

import pytest

from ..driver import ChromeDriver, DriverConfig
from ..reporting import attach_failure

__all__ = ["driver", "webdriver_config", "webdriver_settings"]


@pytest.fixture
def webdriver_settings(request: pytest.FixtureRequest) -> Mapping[str, Any] | DriverConfig:
    """DriverConfig fields, or a ready config. Defaults to an empty dict.

    With indirect parametrize, the value comes from request.param.
    """
    return getattr(request, "param", {})


@pytest.fixture
def webdriver_config(webdriver_settings: Mapping[str, Any] | DriverConfig) -> DriverConfig:
    """Builds a DriverConfig from webdriver_settings. A ready config is returned as is."""
    if isinstance(webdriver_settings, DriverConfig):
        return webdriver_settings
    return DriverConfig(**dict(webdriver_settings))


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item: pytest.Item, call: pytest.CallInfo[None]) -> Iterator[None]:
    outcome: Any = yield
    report = outcome.get_result()
    setattr(item, f"rep_{report.when}", report)


def _failed(node: Any) -> bool:
    """True when setup, the test, or teardown has already failed.

    Setup and call reports exist before this fixture closes. A teardown error in
    an earlier fixture is still on pytest's stack, not in a report yet.
    """
    for phase in ("setup", "call", "teardown"):
        report = getattr(node, f"rep_{phase}", None)
        if report is not None and report.failed:
            return True
    if sys.exc_info()[0] is not None:
        return True
    for frame_info in inspect.stack():
        if frame_info.function != "teardown_exact":
            continue
        if frame_info.frame.f_locals.get("these_exceptions"):
            return True
    return False


@pytest.fixture
def driver(request: pytest.FixtureRequest, webdriver_config: DriverConfig) -> Iterator[ChromeDriver]:
    """A started ChromeDriver. After the test it saves a failure screenshot and trace, then quits."""
    instance = ChromeDriver(webdriver_config)
    instance.start()
    try:
        yield instance
    finally:
        failed = _failed(request.node)
        if failed:
            instance.save_failure_screenshot()
        instance.finish_trace(failed=failed)
        if failed:
            attach_failure(instance)
        instance.quit()
