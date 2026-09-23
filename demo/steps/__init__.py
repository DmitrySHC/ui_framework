from ui_framework import BaseDriver, StepsGroup

from .auth import AuthSteps
from .forms import FormsSteps
from .tables import TablesSteps

__all__ = ["Steps"]


class Steps(StepsGroup):
    """Все шаги проекта: ``auth``, группа ``forms`` и ``tables``."""

    def __init__(self, driver: BaseDriver, base_url: str) -> None:
        super().__init__(driver, base_url)
        self.auth = AuthSteps(driver, base_url)
        self.forms = FormsSteps(driver, base_url)
        self.tables = TablesSteps(driver, base_url)
