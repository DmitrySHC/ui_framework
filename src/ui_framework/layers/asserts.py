from typing import ClassVar

from ..constants.layers import Layer
from .base import Orchestration

__all__ = ["BaseAssert"]


class BaseAssert(Orchestration):
    """Проверки состояния через ``@readonly``-методы одного шага.

    Единственный атрибут — шаг, создаётся в ``__init__``. Внутри методов
    ``AssertionError`` пробрасывается как есть; вызов действия шага, клика,
    ``fill`` или ``open`` поднимает ``LayerError``.
    """

    _layer: ClassVar[Layer] = "assert"
