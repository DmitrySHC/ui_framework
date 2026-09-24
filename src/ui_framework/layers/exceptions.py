from ..driver.exceptions import FrameworkError

__all__ = ["ArchitectureError", "LayerError"]


class LayerError(FrameworkError):
    """A layer was built in the wrong place, holds the wrong child, or a check changed the page."""


class ArchitectureError(LayerError):
    """ensure_architecture found violations. The message lists them."""
