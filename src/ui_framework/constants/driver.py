from pathlib import Path
from typing import Literal

PageLoadStrategy = Literal["normal", "eager", "none"]
TraceMode = Literal["off", "on", "retain-on-failure"]
ColorScheme = Literal["light", "dark", "no-preference"]
GotoWait = Literal["commit", "domcontentloaded", "load"]

ENGINE_NAME = "playwright"

DEFAULT_LOGS_DIR = Path("logs")
DEFAULT_DOWNLOADS_DIR = Path("downloads")
DEFAULT_WINDOW_SIZE = (1600, 1000)
DEFAULT_PAGE_LOAD_TIMEOUT = 60.0
DEFAULT_SCRIPT_TIMEOUT = 30.0
DEFAULT_PAGE_LOAD_STRATEGY: PageLoadStrategy = "normal"
DEFAULT_TRACE_MODE: TraceMode = "off"

#: Чего ждут page.goto и page.reload для каждой стратегии загрузки.
GOTO_WAIT: dict[PageLoadStrategy, GotoWait] = {
    "normal": "load",
    "eager": "domcontentloaded",
    "none": "commit",
}

#: Шаг опроса для ожиданий, которые фреймворк крутит сам (условия элементов, журнал сети).
POLL_INTERVAL = 0.05
