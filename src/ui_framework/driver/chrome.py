from playwright.sync_api import Browser, Playwright

from ..constants.chrome import ALWAYS_ON_ARGUMENTS, BROWSER_LOG_ARGUMENTS, BROWSER_LOG_FILE_ARGUMENT, CHROME_CHANNEL
from .base import BaseDriver
from .config import DriverConfig

__all__ = ["ChromeDriver"]


class ChromeDriver(BaseDriver):
    """Launches the installed Chrome with the config's headless flag, args, and downloads directory."""

    browser_name = "chrome"
    config_class = DriverConfig

    def _launch_browser(self, playwright: Playwright) -> Browser:
        config = self.config
        downloads = config.downloads_dir.expanduser().resolve()
        downloads.mkdir(parents=True, exist_ok=True)
        return playwright.chromium.launch(
            channel=CHROME_CHANNEL,
            headless=config.is_headless,
            args=[*ALWAYS_ON_ARGUMENTS, *config.browser_args, *self._browser_log_arguments()],
            downloads_path=str(downloads),
        )

    def _browser_log_arguments(self) -> tuple[str, ...]:
        return (*BROWSER_LOG_ARGUMENTS, BROWSER_LOG_FILE_ARGUMENT.format(path=self.logs.browser_log))
