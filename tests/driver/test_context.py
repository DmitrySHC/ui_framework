from pathlib import Path

import pytest

from ui_framework import ChromeDriver, DriverConfig, DriverConfigurationError, Geolocation


def test_unknown_color_scheme():
    with pytest.raises(DriverConfigurationError, match="color_scheme"):
        DriverConfig(color_scheme="sepia")


def test_locale_reaches_the_page(tmp_path: Path):
    driver = ChromeDriver(DriverConfig(locale="ru-RU", logs_dir=tmp_path))
    driver.start()
    try:
        driver.open("about:blank")
        assert driver.page.evaluate("() => navigator.language") == "ru-RU"
    finally:
        driver.quit()


def test_storage_state_roundtrip(tmp_path: Path):
    state = tmp_path / "auth.json"
    first = ChromeDriver(DriverConfig(logs_dir=tmp_path / "first"))
    first.start()
    try:
        first.open("about:blank")
        first.save_storage_state(state)
    finally:
        first.quit()
    assert "cookies" in state.read_text(encoding="utf-8")

    second = ChromeDriver(DriverConfig(logs_dir=tmp_path / "second", storage_state=state))
    second.start()
    try:
        second.open("about:blank")
    finally:
        second.quit()


def test_trace_and_screenshot_on_failure(tmp_path: Path):
    driver = ChromeDriver(DriverConfig(trace="retain-on-failure", logs_dir=tmp_path))
    driver.start()
    try:
        driver.open("about:blank")
        driver.save_failure_screenshot()
        driver.finish_trace(failed=True)
    finally:
        driver.quit()
    assert (driver.logs.directory / "trace.zip").is_file()
    assert (driver.logs.directory / "failure.png").is_file()


def test_trace_discarded_when_passed(tmp_path: Path):
    driver = ChromeDriver(DriverConfig(trace="retain-on-failure", logs_dir=tmp_path))
    driver.start()
    try:
        driver.open("about:blank")
        driver.finish_trace(failed=False)
    finally:
        driver.quit()
    assert not (driver.logs.directory / "trace.zip").exists()


def test_geolocation_is_config():
    config = DriverConfig(geolocation=Geolocation(latitude=55.7, longitude=37.6), permissions=("geolocation",))
    assert config.geolocation is not None
    assert config.geolocation.latitude == 55.7
