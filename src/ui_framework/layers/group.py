from typing import Any, ClassVar

from ..constants.layers import Layer, spec
from .base import Orchestration
from .scope import is_root_build, layer_of

__all__ = ["AssertsGroup", "StepsGroup"]


class StepsGroup(Orchestration):
    """Пространство имён для шагов: ``BaseStep``, ``BaseComponentSteps`` и вложенные ``StepsGroup``.

    Корневой экземпляр (создан не из другого слоя) дополнительно принимает
    ``BaseAssert``, ``AssertsGroup`` и объекты без слоя.
    """

    _layer: ClassVar[Layer] = "steps"

    def __setattr__(self, name: str, value: Any) -> None:
        extra = layer_of(value)
        if is_root_build() and (extra is None or spec(extra).extra_on_root):
            object.__setattr__(self, name, value)
            return
        super().__setattr__(name, value)


class AssertsGroup(Orchestration):
    """Пространство имён для проверок: ``BaseAssert``, ``BaseComponentAsserts`` и вложенные ``AssertsGroup``."""

    _layer: ClassVar[Layer] = "asserts"
