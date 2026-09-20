from ..driver.exceptions import FrameworkError

__all__ = ["ArchitectureError", "LayerError"]


class LayerError(FrameworkError):
    """Объект слоя создан не в том конструкторе, хранит чужой слой, или проверка меняет состояние страницы."""


class ArchitectureError(LayerError):
    """``ensure_architecture`` нашла нарушения; текст содержит их список."""
