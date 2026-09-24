import ast
from collections.abc import Iterator
from dataclasses import dataclass
from pathlib import Path

from ..constants.layers import (
    BASE_ASSERT,
    BASE_PAGE,
    ELEMENT_MODULE,
    FRAMEWORK_PACKAGE,
    LAYERS,
    RAW_ACCESS_ATTRIBUTES,
    TESTS_DIR,
    WIDGET_NAMES,
    Layer,
    spec,
)
from .exceptions import ArchitectureError

__all__ = ["Violation", "check_project", "ensure_architecture"]

_SKIP_DIRS = frozenset({"__pycache__", ".venv", "node_modules"})
_LAYER_DIR_NAMES = frozenset(item.directory for item in LAYERS)


@dataclass(frozen=True, slots=True)
class Violation:
    path: Path
    line: int
    rule: str
    message: str

    def __str__(self) -> str:
        return f"{self.path}:{self.line} [{self.rule}] {self.message}"


@dataclass(frozen=True, slots=True)
class _Module:
    path: Path
    tree: ast.Module
    #: Первый каталог относительно корня проекта; "" для файлов в корне.
    top_dir: str


def _iter_modules(root: Path) -> Iterator[_Module]:
    for path in sorted(root.rglob("*.py")):
        relative = path.relative_to(root)
        if any(part in _SKIP_DIRS or part.startswith(".") for part in relative.parts):
            continue
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        top_dir = relative.parts[0] if len(relative.parts) > 1 else ""
        yield _Module(path, tree, top_dir)


def _simple_name(node: ast.expr) -> str | None:
    match node:
        case ast.Name(id=name) | ast.Attribute(attr=name):
            return name
        case ast.Subscript(value=inner):
            return _simple_name(inner)
    return None


def _dir_title(name: str) -> str:
    return f"{name}/" if name else "project root"


class _ClassTable:
    """Maps each project class to a layer by walking its bases."""

    def __init__(self, modules: list[_Module]) -> None:
        self._bases: dict[str, tuple[str, ...]] = {}
        self._locations: dict[str, str] = {}
        self._cache: dict[str, Layer | None] = {item.base: item.name for item in LAYERS}
        for module in modules:
            for node in ast.walk(module.tree):
                if isinstance(node, ast.ClassDef):
                    names = (_simple_name(base) for base in node.bases)
                    self._bases[node.name] = tuple(name for name in names if name is not None)
                    self._locations[node.name] = module.top_dir

    def layer_of(self, name: str) -> Layer | None:
        if name in self._cache:
            return self._cache[name]
        self._cache[name] = None  # защита от циклов в наследовании
        layer: Layer | None = None
        for base in self._bases.get(name, ()):
            layer = self.layer_of(base)
            if layer is not None:
                break
        self._cache[name] = layer
        return layer

    def defined_at_root(self, name: str) -> bool:
        return self._locations.get(name) == ""

    def resolve(self, node: ast.expr) -> tuple[str, Layer] | None:
        """Class name and layer referenced by an expression, or None."""
        name = _simple_name(node)
        if name is None:
            return None
        layer = self.layer_of(name)
        if layer is None:
            return None
        return name, layer


class _ModuleChecker(ast.NodeVisitor):
    def __init__(self, module: _Module, table: _ClassTable, violations: list[Violation]) -> None:
        self._module = module
        self._table = table
        self._violations = violations
        self._classes: list[Layer | None] = []
        self._functions: list[str] = []

    @property
    def _in_tests(self) -> bool:
        return self._module.top_dir == TESTS_DIR

    @property
    def _in_asserts(self) -> bool:
        return self._module.top_dir == BASE_ASSERT.directory

    @property
    def _in_pages(self) -> bool:
        return self._module.top_dir == BASE_PAGE.directory

    def _report(self, node: ast.stmt | ast.expr, rule: str, message: str) -> None:
        self._violations.append(Violation(self._module.path, node.lineno, rule, message))

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        layer = self._table.layer_of(node.name)
        if layer is not None and not spec(layer).lives_in(self._module.top_dir):
            expected, actual = _dir_title(spec(layer).directory), _dir_title(self._module.top_dir)
            self._report(node, "placement", f"{node.name}: {spec(layer).name} lives in {expected}, not {actual}")
        self._classes.append(layer)
        self.generic_visit(node)
        self._classes.pop()

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        self._functions.append(node.name)
        self.generic_visit(node)
        self._functions.pop()

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        self._functions.append(node.name)
        self.generic_visit(node)
        self._functions.pop()

    def visit_Assert(self, node: ast.Assert) -> None:
        if not self._in_asserts:
            self._report(node, "assert", "assert is only allowed in the asserts layer")
        self.generic_visit(node)

    def visit_Name(self, node: ast.Name) -> None:
        if node.id == "AssertionError" and not self._in_asserts:
            self._report(node, "assert", "AssertionError is only allowed in the asserts layer")
        elif node.id in WIDGET_NAMES and not self._in_pages:
            self._report(node, "widgets", f"{node.id}: page elements may only be used in pages/")
        elif self._in_tests and self._table.layer_of(node.id) is not None and not self._table.defined_at_root(node.id):
            self._report(node, "tests", f"{node.id}: tests may only use the root aggregator")
        self.generic_visit(node)

    def visit_Attribute(self, node: ast.Attribute) -> None:
        if node.attr in RAW_ACCESS_ATTRIBUTES and not self._in_pages:
            self._report(node, "driver", f"{node.attr}: only pages may access the driver and raw Locator")
        self.generic_visit(node)

    def visit_Import(self, node: ast.Import) -> None:
        for alias in node.names:
            self._check_import(node, alias.name, frozenset())

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        self._check_import(node, node.module or "", frozenset(alias.name for alias in node.names))

    def _check_import(self, node: ast.stmt, module: str, names: frozenset[str]) -> None:
        widgets = names.intersection(WIDGET_NAMES) if module == FRAMEWORK_PACKAGE else frozenset()
        if not self._in_pages and (widgets or module.startswith(ELEMENT_MODULE)):
            what = ", ".join(sorted(widgets)) or module
            self._report(node, "widgets", f"{what}: page elements may only be imported in pages/")
        forbidden = set(module.split(".")) & _LAYER_DIR_NAMES
        if self._in_tests and forbidden:
            self._report(
                node, "tests", f"tests must not import {', '.join(sorted(forbidden))}: use the root aggregator"
            )

    def visit_Call(self, node: ast.Call) -> None:
        if _simple_name(node.func) == "assert_that" and not self._in_asserts:
            self._report(node, "assert", "assert_that is only allowed in the asserts layer")
        resolved = self._table.resolve(node.func)
        if resolved is not None:
            self._check_construction(node, *resolved)
        self.generic_visit(node)

    def _check_construction(self, node: ast.Call, name: str, layer: Layer) -> None:
        enclosing = self._classes[-1] if self._classes else None
        in_init = bool(self._functions) and self._functions[-1] == "__init__"
        created = spec(layer)
        if in_init and enclosing in created.parents:
            return
        if (
            in_init
            and enclosing is not None
            and spec(enclosing).root
            and created.extra_on_root
            and self._module.top_dir == ""
        ):
            return
        if created.root and self._table.defined_at_root(name) and self._module.top_dir in {"", TESTS_DIR}:
            return
        self._report(node, "construction", f"{name}: {created.name} {created.creation_hint}")


def check_project(root: str | Path) -> list[Violation]:
    """Parses every Python file under root and returns layer violations."""
    modules = list(_iter_modules(Path(root).resolve()))
    table = _ClassTable(modules)
    violations: list[Violation] = []
    for module in modules:
        _ModuleChecker(module, table, violations).visit(module.tree)
    return violations


def ensure_architecture(root: str | Path) -> None:
    """Raises ArchitectureError with the violations from check_project."""
    violations = check_project(root)
    if violations:
        lines = "\n".join(str(violation) for violation in violations)
        raise ArchitectureError(f"layer violations ({len(violations)}):\n{lines}")
