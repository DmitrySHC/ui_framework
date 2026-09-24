BROWSER_LOG_NAME = "browser.log"
CONSOLE_LOG_NAME = "console.log"
SESSION_LOG_NAME = "session.log"

SESSION_LOG_FORMAT = "%(asctime)s %(levelname)-7s %(message)s"
CONSOLE_LOG_LINE = "{level} {message}\n"

#: Run directory name, for example chrome-20260905-145046-14072-01.
LOG_DIR_TIMESTAMP_FORMAT = "%Y%m%d-%H%M%S"
LOG_DIR_NAME_TEMPLATE = "{browser}-{stamp}-{pid}-{index:02d}"
