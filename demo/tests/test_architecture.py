from pathlib import Path

from ui_framework.layers import ensure_architecture

DEMO_ROOT = Path(__file__).resolve().parents[1]


def test_layers_are_respected() -> None:
    ensure_architecture(DEMO_ROOT)
