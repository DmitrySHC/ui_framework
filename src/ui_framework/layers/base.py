from typing import TYPE_CHECKING, Any, ClassVar

from ..constants.layers import Layer, spec
from .exceptions import LayerError
from .scope import LayerMeta, layer_of

if TYPE_CHECKING:
    from ..driver.base import BaseDriver

__all__ = ["Layered", "Orchestration"]


class Layered(metaclass=LayerMeta):
    """Класс со слоем ``_layer``; экземпляры конструирует и проверяет ``LayerMeta``."""

    _layer: ClassVar[Layer | None] = None
    #: True у страниц и компонентов, созданных внутри конструктора шага, проверки или агрегатора.
    _layered: bool = False

    def _layer_built(self) -> None:
        """Вызывается ``LayerMeta`` после ``__init__`` самого внешнего конструктора."""


class Orchestration(Layered):
    """Слой с конструктором ``(driver, base_url)``; в атрибуты принимает только объекты из ``children`` слоя."""

    _layer: ClassVar[Layer]

    def __init__(self, driver: "BaseDriver", base_url: str) -> None:
        """Ничего не сохраняет; дочерние объекты создаёт наследник."""

    def __setattr__(self, name: str, value: Any) -> None:
        allowed = spec(self._layer)
        if layer_of(value) not in allowed.children:
            owner = f"{type(self).__name__}.{name}"
            raise LayerError(f"{owner}: {allowed.holds}, got {type(value).__name__}")
        object.__setattr__(self, name, value)
