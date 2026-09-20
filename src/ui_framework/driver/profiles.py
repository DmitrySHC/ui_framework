from dataclasses import dataclass
from typing import Any

__all__ = ["DEVICE_PROFILES", "DeviceProfile"]


@dataclass(frozen=True, slots=True)
class DeviceProfile:
    """Метрики и User-Agent устройства для мобильной эмуляции."""

    name: str
    width: int
    height: int
    pixel_ratio: float
    user_agent: str
    touch: bool = True

    def context_options(self) -> dict[str, Any]:
        """Аргументы Browser.new_context(...) для эмуляции этого устройства."""
        return {
            "viewport": {"width": self.width, "height": self.height},
            "device_scale_factor": self.pixel_ratio,
            "user_agent": self.user_agent,
            "is_mobile": True,
            "has_touch": self.touch,
        }


DEVICE_PROFILES: dict[str, DeviceProfile] = {
    "Pixel 5": DeviceProfile(
        name="Pixel 5",
        width=393,
        height=851,
        pixel_ratio=2.75,
        user_agent=(
            "Mozilla/5.0 (Linux; Android 14; Pixel 5) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/151.0.0.0 Mobile Safari/537.36"
        ),
    ),
    "iPhone 12 Pro": DeviceProfile(
        name="iPhone 12 Pro",
        width=390,
        height=844,
        pixel_ratio=3.0,
        user_agent=(
            "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 "
            "(KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1"
        ),
    ),
    "Galaxy S20": DeviceProfile(
        name="Galaxy S20",
        width=360,
        height=800,
        pixel_ratio=3.0,
        user_agent=(
            "Mozilla/5.0 (Linux; Android 13; SM-G981B) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/151.0.0.0 Mobile Safari/537.36"
        ),
    ),
}
