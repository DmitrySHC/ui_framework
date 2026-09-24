from typing import ClassVar

from ..constants.layers import Layer
from .base import Orchestration

__all__ = ["BaseComponentSteps"]


class BaseComponentSteps(Orchestration):
    """Действия над общим фрагментом UI.

    Создаётся в конструкторе шага (или агрегатора шагов), которому фрагмент
    нужен, либо в конструкторе парной ``BaseComponentAsserts``. Атрибуты —
    только компоненты. Методы без ``@readonly`` недоступны из проверок.
    """

    _layer: ClassVar[Layer] = "component_step"
