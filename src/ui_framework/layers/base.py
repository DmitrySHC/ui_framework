from typing import TYPE_CHECKING, Any, ClassVar

from ..constants.layers import Layer, spec
from .exceptions import LayerError
from .scope import LayerMeta, layer_of

if TYPE_CHECKING:
    from ..driver.base import BaseDriver

__all__ = ["Layered", "Orchestration"]


class Layered(metaclass=LayerMeta):
    """A class with a layer. LayerMeta checks where its instances are built."""

    _layer: ClassVar[Layer | None] = None
    #: True for a page or component built inside a step, check, or group constructor.
    _layered: bool = False

    def _layer_built(self) -> None:
        """Called by LayerMeta after the outermost constructor finishes."""


class Orchestration(Layered):
    """A layer built from driver and base_url. Attributes must be its child layers."""

    _layer: ClassVar[Layer]

    def __init__(self, driver: "BaseDriver", base_url: str) -> None:
        """Stores nothing. The subclass creates the children."""

    def __setattr__(self, name: str, value: Any) -> None:
        allowed = spec(self._layer)
        if layer_of(value) not in allowed.children:
            owner = f"{type(self).__name__}.{name}"
            raise LayerError(f"{owner}: {allowed.holds}, got {type(value).__name__}")
        object.__setattr__(self, name, value)
