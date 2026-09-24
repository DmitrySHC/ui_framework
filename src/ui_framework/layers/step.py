from typing import ClassVar

from ..constants.layers import Layer
from .base import Orchestration

__all__ = ["BaseStep"]


class BaseStep(Orchestration):
    """Действия над страницами, компонентами и шагами компонентов.

    Атрибуты создаются в ``__init__``. Из методов доступны методы этих
    объектов; обращение к их элементам или ``driver`` поднимает ``LayerError``.
    Методы без ``@readonly`` считаются действиями и недоступны из проверок.
    """

    _layer: ClassVar[Layer] = "step"
