#: Установленный Chrome, а не Chromium из комплекта Playwright.
CHROME_CHANNEL = "chrome"

#: Всегда передаём в Chrome.
ALWAYS_ON_ARGUMENTS = (
    "--no-sandbox",
    "--disable-dev-shm-usage",
    "--disable-gpu",
)

#: Логирование процесса браузера; путь к файлу подставляется драйвером.
BROWSER_LOG_ARGUMENTS = ("--enable-logging", "--v=1")
BROWSER_LOG_FILE_ARGUMENT = "--log-file={path}"
