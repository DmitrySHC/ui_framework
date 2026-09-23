from ui_framework import BasePage, url
from ui_framework.driver import ChromeDriver

_BASE = "https://example.com"


@url("/login")
class LoginPage(BasePage):
    pass


class InheritedLoginPage(LoginPage):
    pass


@url("/logout")
class LogoutPage(LoginPage):
    pass


@url("/users/{user}/posts/{post}")
class PostPage(BasePage):
    pass


@url("https://example.com/absolute/{user}")
class AbsolutePage(BasePage):
    pass


def test_builds_url_from_path(driver: ChromeDriver):
    page = LoginPage(driver, _BASE)
    assert page.url() == "https://example.com/login"


def test_inherits_path(driver: ChromeDriver):
    page = InheritedLoginPage(driver, _BASE)
    assert page.url() == "https://example.com/login"


def test_override_path(driver: ChromeDriver):
    page = LogoutPage(driver, _BASE)
    assert page.url() == "https://example.com/logout"


def test_substitutes_placeholders(driver: ChromeDriver):
    page = PostPage(driver, _BASE)
    assert page.url(user="alice", post="42") == "https://example.com/users/alice/posts/42"


def test_quotes_path_values(driver: ChromeDriver):
    page = PostPage(driver, _BASE)
    built = page.url(user="a b", post="x/y")
    assert built == "https://example.com/users/a%20b/posts/x%2Fy"


def test_absolute_template(driver: ChromeDriver):
    page = AbsolutePage(driver, "https://ignored.example")
    assert page.url(user="alice") == "https://example.com/absolute/alice"
