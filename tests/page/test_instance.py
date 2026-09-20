from ui_framework import BaseInstance
from ui_framework.driver import ChromeDriver


def test_stores_driver(driver: ChromeDriver) -> None:
    instance = BaseInstance(driver)
    assert instance.driver is driver
