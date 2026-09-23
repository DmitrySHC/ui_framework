import pytest

from ui_framework import ChromeDriver, DriverConfig, DriverNotStartedError


def test_intercept_before_start_raises():
    driver = ChromeDriver(DriverConfig())
    try:
        with pytest.raises(DriverNotStartedError), driver.network.intercept():
            pass
    finally:
        driver.quit()
