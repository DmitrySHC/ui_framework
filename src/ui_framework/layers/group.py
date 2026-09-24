from typing import Any, ClassVar

from ..constants.layers import Layer, spec
from .base import Orchestration
from .scope import is_root_build, layer_of

__all__ = ["AssertsGroup", "StepsGroup"]


class StepsGroup(Orchestration):
    """Namespace for steps, component steps, and nested step groups.

    The root instance, built outside any layer, may also hold checks and plain objects.
    """

    _layer: ClassVar[Layer] = "steps"

    def __setattr__(self, name: str, value: Any) -> None:
        extra = layer_of(value)
        if is_root_build() and (extra is None or spec(extra).extra_on_root):
            object.__setattr__(self, name, value)
            return
        super().__setattr__(name, value)


class AssertsGroup(Orchestration):
    """Namespace for checks, component checks, and nested check groups."""

    _layer: ClassVar[Layer] = "asserts"
