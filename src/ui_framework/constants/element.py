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

#: Поиск через ``page.get_by_*``, не через CSS-шаблон.
QUERY_LOCATORS: tuple[str, ...] = (
    "role",
    "label",
    "placeholder",
    "text",
    "test_id",
    "alt_text",
    "title",
)
#: ``exact`` имеет смысл только у этих способов поиска.
EXACT_LOCATORS: frozenset[str] = frozenset({"role", "label", "placeholder", "text", "alt_text", "title"})

WAIT_TIMEOUT_MESSAGE = "{label}: timed out waiting for {what} after {seconds}s"
