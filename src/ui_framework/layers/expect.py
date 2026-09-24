from collections.abc import Callable

from ..element.exceptions import ConditionNotMatchedException

__all__ = ["as_assertion"]


def as_assertion(wait: Callable[[], object]) -> None:
    """Run a wait used by a check. A timeout becomes AssertionError."""
    try:
        wait()
    except ConditionNotMatchedException as error:
        raise AssertionError(str(error)) from error
