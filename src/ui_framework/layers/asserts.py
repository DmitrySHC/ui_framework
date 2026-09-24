from collections.abc import Callable
from typing import ClassVar

from ..constants.layers import Layer
from .base import Orchestration
from .expect import as_assertion
from .session import step_of

__all__ = ["BaseAssert"]


class BaseAssert(Orchestration):
    """Checks state through readonly methods of its step.

    Init creates the step and any component checks. AssertionError is kept.
    A click, fill, open, or other action raises LayerError.
    """

    _layer: ClassVar[Layer] = "assert"

    def current_url(self) -> str:
        """URL of the open tab, read through this check's step."""
        return step_of(self).current_url()

    def title(self) -> str:
        """Title of the open tab, read through this check's step."""
        return step_of(self).title()

    def check(self, wait: Callable[[], object]) -> None:
        """Run a readonly wait. A missed condition becomes AssertionError."""
        as_assertion(wait)
