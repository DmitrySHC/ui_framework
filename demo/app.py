from ui_framework import BaseDriver, StepsGroup

from demo.asserts import Asserts
from demo.steps import Steps

__all__ = ["BASE_URL", "TheInternet"]

BASE_URL = "https://the-internet.herokuapp.com"


class TheInternet(StepsGroup):
    """Корневой агрегатор the-internet: ``steps`` выполняют сценарии, ``asserts`` проверяют результат."""

    def __init__(self, driver: BaseDriver, base_url: str) -> None:
        super().__init__(driver, base_url)
        self.steps = Steps(driver, base_url)
        self.asserts = Asserts(driver, base_url)
