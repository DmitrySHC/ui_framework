DEFAULT_ELEMENT_WAIT = 10.0

#: Локатор -> селектор Playwright. Ключи — допустимые kwargs BaseElement.
LOCATOR_TEMPLATES: dict[str, str] = {
    "css": "{}",
    "id": "#{}",
    "xpath": "xpath={}",
    "name": '[name="{}"]',
    "class_name": ".{}",
    "tag": "{}",
}
LOCATOR_FIELDS = tuple(LOCATOR_TEMPLATES)

WAIT_TIMEOUT_MESSAGE = "{label}: timed out waiting for {what} after {seconds}s"
