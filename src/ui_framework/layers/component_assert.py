from typing import ClassVar

from ..constants.layers import Layer
from .base import Orchestration

__all__ = ["BaseComponentAsserts"]


class BaseComponentAsserts(Orchestration):
    """Checks for one shared UI fragment.

    Built by the assert or group that needs it. It holds only the component step.
    """

    _layer: ClassVar[Layer] = "component_assert"
