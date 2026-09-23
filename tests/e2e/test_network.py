from ui_framework.driver import ChromeDriver

from .the_internet import BASE_URL, DropdownPage, LoginPage, StubbedPage

STUB_BODY = "<!DOCTYPE html><html><body><h1 id='stubbed'>stubbed response</h1></body></html>"


def test_intercept_records_document_request(driver: ChromeDriver):
    login = LoginPage(driver, BASE_URL)
    with driver.network.intercept("**/login") as log:
        login.open()
        seen = log.wait_for("/login")

    assert seen.method == "GET"
    assert "the-internet.herokuapp.com/login" in seen.url


def test_stub_replaces_document(driver: ChromeDriver):
    page = StubbedPage(driver, BASE_URL)
    with driver.network.stub("**/dropdown", body=STUB_BODY):
        page.open()
        assert page.heading.text == "stubbed response"


def test_stub_is_removed_after_context(driver: ChromeDriver):
    stubbed = StubbedPage(driver, BASE_URL)
    with driver.network.stub("**/dropdown", body=STUB_BODY):
        stubbed.open()
        assert stubbed.heading.text == "stubbed response"

    real = DropdownPage(driver, BASE_URL).open()
    assert "Dropdown" in real.heading.text


def test_rewrite_sends_request_to_another_url(driver: ChromeDriver):
    login = LoginPage(driver, BASE_URL)
    dropdown = DropdownPage(driver, BASE_URL)
    with driver.network.rewrite("**/dropdown", to=login.url()):
        driver.open(dropdown.url())
        login.wait_loaded()

    assert "Login Page" in login.heading.text
    assert "dropdown" in login.current_url
