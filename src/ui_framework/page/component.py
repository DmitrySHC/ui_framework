from typing import ClassVar

from ..constants.layers import Layer
from .instance import BaseInstance

__all__ = ["BaseComponent"]


class BaseComponent(BaseInstance):
    """Фрагмент UI без URL: баннер, шапка, модалка.

    Создаётся в конструкторе страницы, шага сценария или шага компонента.
    """

    _layer: ClassVar[Layer | None] = "component"
