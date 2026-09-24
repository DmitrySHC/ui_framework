#: Installed Chrome, not the Chromium bundled with Playwright.
CHROME_CHANNEL = "chrome"

#: Always passed to Chrome.
ALWAYS_ON_ARGUMENTS = (
    "--no-sandbox",
    "--disable-dev-shm-usage",
    "--disable-gpu",
)

#: Browser process logging. The driver fills in the log file path.
BROWSER_LOG_ARGUMENTS = ("--enable-logging", "--v=1")
BROWSER_LOG_FILE_ARGUMENT = "--log-file={path}"
