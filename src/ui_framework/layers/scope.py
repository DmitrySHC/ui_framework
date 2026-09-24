import functools
from abc import ABCMeta
from collections.abc import Callable, Iterator, Mapping
from contextlib import contextmanager
from contextvars import ContextVar
from dataclasses import dataclass
from types import FunctionType
from typing import Any, cast

from ..constants.layers import Kind, Layer, spec
from .exceptions import LayerError

__all__ = [
    "LayerMeta",
    "ensure_inside_elements",
    "ensure_mutable",
    "is_root_build",
    "layer_of",
    "mutating",
    "readonly",
]

_READONLY_MARK = "__layer_readonly__"


@dataclass(frozen=True, slots=True)
class Frame:
    kind: Kind
    layer: Layer


_stack: ContextVar[tuple[Frame, ...]] = ContextVar("ui_framework_layers", default=())


@contextmanager
def _frame(kind: Kind, layer: Layer) -> Iterator[None]:
    token = _stack.set((*_stack.get(), Frame(kind, layer)))
    try:
        yield
    finally:
        _stack.reset(token)


def layer_of(value: object) -> Layer | None:
    """Слой объекта по маркеру класса; None для обычных объектов."""
    return getattr(type(value), "_layer", None)


def is_root_build() -> bool:
    """True, пока выполняется конструктор корневого агрегатора (в стеке один кадр ``build`` с ``root``)."""
    stack = _stack.get()
    return len(stack) == 1 and stack[0].kind == "build" and spec(stack[0].layer).root


def readonly[F: Callable[..., Any]](func: F) -> F:
    """Помечает метод как чтение состояния: его можно вызывать из слоя проверок."""
    setattr(func, _READONLY_MARK, True)
    return func


def mutating[F: Callable[..., Any]](func: F) -> F:
    """Оборачивает метод элемента проверкой ``ensure_mutable`` перед вызовом."""

    @functools.wraps(func)
    def wrapper(self: Any, *args: Any, **kwargs: Any) -> Any:
        ensure_mutable(f"{self.label}.{func.__name__}")
        return func(self, *args, **kwargs)

    return cast(F, wrapper)


def ensure_mutable(what: str) -> None:
    """Поднимает ``LayerError``, если в стеке вызовов есть слой проверок."""
    if any(spec(frame.layer).read_only for frame in _stack.get()):
        raise LayerError(f"{what}: asserts layer is read-only")


def ensure_inside_elements(what: str) -> None:
    """Поднимает ``LayerError``, если текущий вызов — не метод страницы или компонента."""
    stack = _stack.get()
    if not stack or not spec(stack[-1].layer).elements:
        raise LayerError(f"{what}: only page and component methods may use elements")


def _check_parent(name: str, layer: Layer) -> None:
    stack = _stack.get()
    if not stack:
        return
    top = stack[-1]
    created = spec(layer)
    if top.kind == "build" and top.layer in created.parents:
        return
    if created.extra_on_root and is_root_build():
        return
    where = f"{top.kind} of {top.layer}"
    raise LayerError(f"{name}: {created.name} {created.creation_hint}, currently {where}")


def _wrap_function(func: Callable[..., Any], layer: Layer, *, guard_mutation: bool) -> Callable[..., Any]:
    converts_assertions = not spec(layer).read_only

    @functools.wraps(func)
    def wrapper(self: Any, *args: Any, **kwargs: Any) -> Any:
        if guard_mutation:
            ensure_mutable(f"{type(self).__name__}.{func.__name__}")
        with _frame("call", layer):
            try:
                return func(self, *args, **kwargs)
            except AssertionError as error:
                if not converts_assertions:
                    raise
                message = f"{type(self).__name__}.{func.__name__}: AssertionError is only allowed in the asserts layer"
                raise LayerError(message) from error

    return wrapper


def _wrap_members(cls: type, namespace: Mapping[str, Any], layer: Layer) -> None:
    actions = spec(layer).guards_writes
    for name, member in namespace.items():
        if name.startswith("_"):
            continue
        if isinstance(member, property) and member.fget is not None:
            fget = _wrap_function(member.fget, layer, guard_mutation=False)
            fset = None if member.fset is None else _wrap_function(member.fset, layer, guard_mutation=actions)
            setattr(cls, name, property(fget, fset, member.fdel, member.__doc__))
        elif isinstance(member, FunctionType):
            guard = actions and not getattr(member, _READONLY_MARK, False)
            setattr(cls, name, _wrap_function(member, layer, guard_mutation=guard))


class LayerMeta(ABCMeta):
    """Ведёт стек кадров слоёв.

    При создании класса оборачивает его публичные методы и свойства: вызов кладёт
    кадр ``call``, а ``AssertionError`` вне слоя проверок превращает в ``LayerError``.
    При создании экземпляра сверяет верх стека с ``parents`` слоя, держит кадр
    ``build`` на время ``__init__`` и затем вызывает ``_layer_built``. Для классов с
    ``_layer = None`` ничего не делает.
    """

    _layer: Layer | None

    def __new__(mcls, name: str, bases: tuple[type, ...], namespace: dict[str, Any], **kwargs: Any) -> "LayerMeta":
        cls = super().__new__(mcls, name, bases, namespace, **kwargs)
        if cls._layer is not None and spec(cls._layer).call_scoped:
            _wrap_members(cls, namespace, cls._layer)
        return cls

    def __call__(cls, *args: Any, **kwargs: Any) -> Any:
        layer = cls._layer
        if layer is None:
            return super().__call__(*args, **kwargs)
        _check_parent(cls.__name__, layer)
        layered = any(spec(frame.layer).orchestration for frame in _stack.get())
        with _frame("build", layer):
            instance = super().__call__(*args, **kwargs)
        if spec(layer).elements:
            object.__setattr__(instance, "_layered", layered)
        instance._layer_built()
        return instance
