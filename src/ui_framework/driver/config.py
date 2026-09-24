from pathlib import Path
from typing import Annotated, Any, Self

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    StrictBool,
    StringConstraints,
    ValidationError,
    field_validator,
    model_validator,
)

from ..constants.devices import DEFAULT_DEVICE
from ..constants.driver import (
    DEFAULT_DOWNLOADS_DIR,
    DEFAULT_LOGS_DIR,
    DEFAULT_PAGE_LOAD_STRATEGY,
    DEFAULT_PAGE_LOAD_TIMEOUT,
    DEFAULT_SCRIPT_TIMEOUT,
    DEFAULT_TRACE_MODE,
    DEFAULT_WINDOW_SIZE,
    ColorScheme,
    PageLoadStrategy,
    TraceMode,
)
from .exceptions import DriverConfigurationError
from .profiles import DEVICE_PROFILES

__all__ = ["DriverConfig", "Geolocation"]

PositiveSeconds = Annotated[float, Field(gt=0, strict=True)]
PositiveInt = Annotated[int, Field(gt=0, strict=True)]
BrowserArgument = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]


def _format_validation_error(error: ValidationError) -> str:
    parts: list[str] = []
    for item in error.errors():
        message = item["msg"].removeprefix("Value error, ")
        location = ".".join(str(part) for part in item["loc"])
        parts.append(f"{location}: {message}" if location else message)
    return "; ".join(parts)


class Geolocation(BaseModel):
    """Latitude and longitude passed to the browser context."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    latitude: float
    longitude: float


class DriverConfig(BaseModel):
    """How to launch the browser.

    An unknown field, a bad type, an unknown device, or device without
    is_mobile raises DriverConfigurationError. is_mobile without a device uses
    the default device. is_incognito does nothing: each context is already isolated.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    is_headless: StrictBool = False
    is_mobile: StrictBool = False
    is_incognito: StrictBool = False
    device: str | None = None
    window_size: tuple[PositiveInt, PositiveInt] = DEFAULT_WINDOW_SIZE
    browser_args: tuple[BrowserArgument, ...] = ()
    logs_dir: Path = DEFAULT_LOGS_DIR
    downloads_dir: Path = DEFAULT_DOWNLOADS_DIR
    page_load_timeout: PositiveSeconds = DEFAULT_PAGE_LOAD_TIMEOUT
    script_timeout: PositiveSeconds = DEFAULT_SCRIPT_TIMEOUT
    page_load_strategy: PageLoadStrategy = DEFAULT_PAGE_LOAD_STRATEGY
    trace: TraceMode = DEFAULT_TRACE_MODE
    storage_state: Path | None = None
    locale: str | None = None
    timezone_id: str | None = None
    color_scheme: ColorScheme | None = None
    geolocation: Geolocation | None = None
    permissions: tuple[str, ...] = ()

    def __init__(self, **data: Any) -> None:
        try:
            super().__init__(**data)
        except ValidationError as error:
            raise DriverConfigurationError(_format_validation_error(error)) from error

    @model_validator(mode="before")
    @classmethod
    def _default_mobile_device(cls, data: Any) -> Any:
        if isinstance(data, dict) and data.get("is_mobile") and data.get("device") is None:
            return {**data, "device": DEFAULT_DEVICE}
        return data

    @field_validator("device")
    @classmethod
    def _known_device(cls, device: str | None) -> str | None:
        if device is None or device in DEVICE_PROFILES:
            return device
        raise ValueError(f"Unknown device {device!r}. Available: {sorted(DEVICE_PROFILES)}")

    @model_validator(mode="after")
    def _device_requires_mobile(self) -> Self:
        if self.device is not None and not self.is_mobile:
            raise ValueError(f"device={self.device!r} passed without is_mobile=True: mobile emulation is ambiguous")
        return self
