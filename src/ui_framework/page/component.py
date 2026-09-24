from typing import ClassVar

from ..constants.layers import Layer
from .instance import BaseInstance

__all__ = ["BaseComponent"]


class BaseComponent(BaseInstance):
    """A piece of UI without its own URL, such as a banner, header, or modal.

    Created in a page, a scenario step, or a component step.
    """

    _layer: ClassVar[Layer | None] = "component"
