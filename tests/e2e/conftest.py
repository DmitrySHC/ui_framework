import pytest


@pytest.fixture
def webdriver_settings() -> dict[str, object]:
    return {"is_incognito": True}
