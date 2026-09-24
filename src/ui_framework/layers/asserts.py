from typing import ClassVar

from ..constants.layers import Layer
from .base import Orchestration

__all__ = ["BaseAssert"]


class BaseAssert(Orchestration):
    """Проверки состояния через ``@readonly``-методы шага своего домена.

    В ``__init__`` создаёт шаг и, если нужны, проверки компонентов.
    ``AssertionError`` пробрасывается как есть; вызов действия шага, клика,
    ``fill`` или ``open`` поднимает ``LayerError``.
    """

    _layer: ClassVar[Layer] = "assert"
