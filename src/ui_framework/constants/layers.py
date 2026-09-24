from dataclasses import dataclass
from typing import Literal

Layer = Literal[
    "component",
    "page",
    "component_step",
    "step",
    "component_assert",
    "assert",
    "steps",
    "asserts",
]
Kind = Literal["build", "call"]

TESTS_DIR = "tests"
FRAMEWORK_PACKAGE = "ui_framework"
ELEMENT_MODULE = f"{FRAMEWORK_PACKAGE}.element"

WIDGET_NAMES: tuple[str, ...] = (
    "BaseElement",
    "Button",
    "Checkbox",
    "Image",
    "Link",
    "RadioButton",
    "Select",
    "Text",
    "TextInput",
)
RAW_ACCESS_ATTRIBUTES: tuple[str, ...] = ("driver", "web_element")


@dataclass(frozen=True, slots=True, kw_only=True)
class LayerSpec:
    """Rules for one layer: directory, who may create it, what it may store."""

    name: Layer
    directory: str
    base: str
    parents: tuple[Layer, ...]
    children: tuple[Layer, ...] = ()
    call_scoped: bool = False
    orchestration: bool = False
    elements: bool = False
    extra_on_root: bool = False
    root: bool = False
    read_only: bool = False

    def lives_in(self, top_dir: str) -> bool:
        return top_dir == self.directory or (self.root and top_dir == "")

    @property
    def creation_hint(self) -> str:
        if self.extra_on_root:
            parents = " or ".join(sorted(self.parents))
            return f"must be created in a {parents} constructor or the root steps group"
        if not self.parents:
            return "must be created at the top level"
        parents = " or ".join(sorted(self.parents))
        return f"must be created in a {parents} constructor"

    @property
    def holds(self) -> str:
        allowed = " or ".join(self.children) if self.children else "nothing"
        return f"{self.name} may only hold {allowed}"

    @property
    def guards_writes(self) -> bool:
        return self.call_scoped and self.orchestration and not self.read_only


BASE_COMPONENT = LayerSpec(
    name="component",
    directory="pages",
    base="BaseComponent",
    parents=("page", "step", "component_step"),
    call_scoped=True,
    elements=True,
)
BASE_PAGE = LayerSpec(
    name="page",
    directory="pages",
    base="BasePage",
    parents=("step",),
    call_scoped=True,
    elements=True,
)
BASE_COMPONENT_STEP = LayerSpec(
    name="component_step",
    directory="steps",
    base="BaseComponentSteps",
    parents=("step", "component_assert", "steps"),
    children=("component",),
    call_scoped=True,
    orchestration=True,
)
BASE_STEP = LayerSpec(
    name="step",
    directory="steps",
    base="BaseStep",
    parents=("assert", "steps"),
    children=("page", "component", "component_step"),
    call_scoped=True,
    orchestration=True,
)
BASE_COMPONENT_ASSERT = LayerSpec(
    name="component_assert",
    directory="asserts",
    base="BaseComponentAsserts",
    parents=("assert", "asserts"),
    children=("component_step",),
    call_scoped=True,
    orchestration=True,
    read_only=True,
)
BASE_ASSERT = LayerSpec(
    name="assert",
    directory="asserts",
    base="BaseAssert",
    parents=("asserts",),
    children=("step", "component_assert"),
    call_scoped=True,
    orchestration=True,
    extra_on_root=True,
    read_only=True,
)
STEPS_GROUP = LayerSpec(
    name="steps",
    directory="steps",
    base="StepsGroup",
    parents=("steps",),
    children=("step", "component_step", "steps"),
    orchestration=True,
    root=True,
)
ASSERTS_GROUP = LayerSpec(
    name="asserts",
    directory="asserts",
    base="AssertsGroup",
    parents=("asserts",),
    children=("assert", "component_assert", "asserts"),
    orchestration=True,
    extra_on_root=True,
)

LAYERS: tuple[LayerSpec, ...] = (
    BASE_COMPONENT,
    BASE_PAGE,
    BASE_COMPONENT_STEP,
    BASE_STEP,
    BASE_COMPONENT_ASSERT,
    BASE_ASSERT,
    STEPS_GROUP,
    ASSERTS_GROUP,
)


def spec(layer: Layer) -> LayerSpec:
    match layer:
        case "component":
            return BASE_COMPONENT
        case "page":
            return BASE_PAGE
        case "component_step":
            return BASE_COMPONENT_STEP
        case "step":
            return BASE_STEP
        case "component_assert":
            return BASE_COMPONENT_ASSERT
        case "assert":
            return BASE_ASSERT
        case "steps":
            return STEPS_GROUP
        case "asserts":
            return ASSERTS_GROUP
