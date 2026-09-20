from ui_framework import AssertsGroup, BaseDriver

from .checkboxes import CheckboxesAsserts
from .dropdown import DropdownAsserts

__all__ = ["FormsAsserts"]


class FormsAsserts(AssertsGroup):
    def __init__(self, driver: BaseDriver, base_url: str) -> None:
        super().__init__(driver, base_url)
        self.dropdown = DropdownAsserts(driver, base_url)
        self.checkboxes = CheckboxesAsserts(driver, base_url)
