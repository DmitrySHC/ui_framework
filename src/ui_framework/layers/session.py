from typing import Protocol

from ..page.component import BaseComponent
from ..page.page import BasePage
from .exceptions import LayerError

__all__ = ["browser_of", "step_of"]


class _Tab(Protocol):
    @property
    def current_url(self) -> str: ...

    @property
    def title(self) -> str: ...


class _SessionStep(Protocol):
    def current_url(self) -> str: ...

    def title(self) -> str: ...


def browser_of(owner: object) -> _Tab:
    """First page or component held by a step. The tab is the same for all of them."""
    for value in vars(owner).values():
        if isinstance(value, (BasePage, BaseComponent)):
            return value
    raise LayerError(f"{type(owner).__name__} holds no page or component")


def step_of(owner: object) -> _SessionStep:
    """First step held by a check."""
    from .component_step import BaseComponentSteps
    from .step import BaseStep

    for value in vars(owner).values():
        if isinstance(value, (BaseStep, BaseComponentSteps)):
            return value
    raise LayerError(f"{type(owner).__name__} holds no step")
