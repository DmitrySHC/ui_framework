from ui_framework import BaseDriver, StepsGroup

from .checkboxes import CheckboxesSteps
from .dropdown import DropdownSteps

__all__ = ["FormsSteps"]


class FormsSteps(StepsGroup):
    """Шаги страниц с формами: ``dropdown`` и ``checkboxes``."""

    def __init__(self, driver: BaseDriver, base_url: str) -> None:
        super().__init__(driver, base_url)
        self.dropdown = DropdownSteps(driver, base_url)
        self.checkboxes = CheckboxesSteps(driver, base_url)
