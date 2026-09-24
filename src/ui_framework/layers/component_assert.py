from typing import ClassVar

from ..constants.layers import Layer
from .base import Orchestration

__all__ = ["BaseComponentAsserts"]


class BaseComponentAsserts(Orchestration):
    """Проверки общего фрагмента UI через ``@readonly``-методы его шага.

    Создаётся в конструкторе проверки (или агрегатора проверок), которой
    фрагмент нужен. Единственный атрибут — ``BaseComponentSteps``.
    """

    _layer: ClassVar[Layer] = "component_assert"
