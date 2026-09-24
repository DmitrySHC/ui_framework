DEFAULT_ELEMENT_WAIT = 10.0

#: Locator field to a Playwright selector. Keys are the allowed BaseElement arguments.
LOCATOR_TEMPLATES: dict[str, str] = {
    "css": "{}",
    "id": "#{}",
    "xpath": "xpath={}",
    "name": '[name="{}"]',
    "class_name": ".{}",
    "tag": "{}",
}
LOCATOR_FIELDS = tuple(LOCATOR_TEMPLATES)

#: Found with page.get_by_*, not a CSS template.
QUERY_LOCATORS: tuple[str, ...] = (
    "role",
    "label",
    "placeholder",
    "text",
    "test_id",
    "alt_text",
    "title",
)
#: exact is valid only for these locator fields.
EXACT_LOCATORS: frozenset[str] = frozenset({"role", "label", "placeholder", "text", "alt_text", "title"})

WAIT_TIMEOUT_MESSAGE = "{label}: timed out waiting for {what} after {seconds}s"
