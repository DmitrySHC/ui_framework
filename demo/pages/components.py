from ui_framework import BaseComponent, Text

__all__ = ["FlashMessage"]


class FlashMessage(BaseComponent):
    """Блок ``#flash`` с результатом последнего действия."""

    banner = Text(id="flash")

    def message(self) -> str:
        return self.banner.text.strip()
