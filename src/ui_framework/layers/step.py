from typing import ClassVar

from ..constants.layers import Layer
from .base import Orchestration

__all__ = ["BaseStep"]


class BaseStep(Orchestration):
    """Действия над одной или несколькими страницами.

    Атрибуты — только страницы, создаются в ``__init__``. Из методов доступны
    методы страниц; обращение к их элементам или ``driver`` поднимает ``LayerError``.
    Методы без ``@readonly`` считаются действиями и недоступны из ``BaseAssert``.
    """

    _layer: ClassVar[Layer] = "step"
