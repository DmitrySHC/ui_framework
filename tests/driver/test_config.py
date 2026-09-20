from typing import Any

import pytest

from ui_framework import DriverConfig, DriverConfigurationError


def test_unknown_field_raises() -> None:
    settings: dict[str, Any] = {"not_a_field": True}
    with pytest.raises(DriverConfigurationError, match="Extra inputs are not permitted"):
        DriverConfig(**settings)
