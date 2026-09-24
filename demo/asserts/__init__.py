from ui_framework import AssertsGroup, BaseDriver

from .auth import AuthAsserts
from .forms import FormsAsserts
from .tables import TablesAsserts

__all__ = ["Asserts"]


class Asserts(AssertsGroup):
    """Project checks: auth, forms, and tables."""

    def __init__(self, driver: BaseDriver, base_url: str) -> None:
        super().__init__(driver, base_url)
        self.auth = AuthAsserts(driver, base_url)
        self.forms = FormsAsserts(driver, base_url)
        self.tables = TablesAsserts(driver, base_url)
