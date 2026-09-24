from typing import ClassVar

from ..constants.layers import Layer
from .base import Orchestration

__all__ = ["BaseComponentSteps"]


class BaseComponentSteps(Orchestration):
    """Actions for one shared UI fragment.

    Built by the step or group that needs it, or by its component check.
    It holds only components. Methods without readonly are hidden from checks.
    """

    _layer: ClassVar[Layer] = "component_step"
