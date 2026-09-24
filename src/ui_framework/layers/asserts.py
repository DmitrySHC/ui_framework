from typing import ClassVar

from ..constants.layers import Layer
from .base import Orchestration

__all__ = ["BaseAssert"]


class BaseAssert(Orchestration):
    """Checks state through readonly methods of its step.

    Init creates the step and any component checks. AssertionError is kept.
    A click, fill, open, or other action raises LayerError.
    """

    _layer: ClassVar[Layer] = "assert"
