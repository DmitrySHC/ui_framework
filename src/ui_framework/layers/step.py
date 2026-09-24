from typing import ClassVar

from ..constants.layers import Layer
from .base import Orchestration

__all__ = ["BaseStep"]


class BaseStep(Orchestration):
    """Actions over pages, components, and component steps.

    Children are created in init. Methods may call those objects, but not their
    elements or driver. A method without readonly is an action and is hidden from checks.
    """

    _layer: ClassVar[Layer] = "step"
