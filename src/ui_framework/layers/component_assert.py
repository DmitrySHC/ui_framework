from collections.abc import Callable
from typing import ClassVar

from ..constants.layers import Layer
from .base import Orchestration
from .expect import as_assertion
from .session import step_of

__all__ = ["BaseComponentAsserts"]


class BaseComponentAsserts(Orchestration):
    """Checks for one shared UI fragment.

    Built by the assert or group that needs it. It holds only the component step.
    """

    _layer: ClassVar[Layer] = "component_assert"

    def current_url(self) -> str:
        """URL of the open tab, read through this check's step."""
        return step_of(self).current_url()

    def title(self) -> str:
        """Title of the open tab, read through this check's step."""
        return step_of(self).title()

    def check(self, wait: Callable[[], object]) -> None:
        """Run a readonly wait. A missed condition becomes AssertionError."""
        as_assertion(wait)
