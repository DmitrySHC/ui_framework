from typing import ClassVar

from ..constants.layers import Layer
from .instance import BaseInstance

__all__ = ["BaseComponent"]


class BaseComponent(BaseInstance):
    """Часть страницы без собственного URL и навигации; создаётся в конструкторе страницы."""

    _layer: ClassVar[Layer | None] = "component"
