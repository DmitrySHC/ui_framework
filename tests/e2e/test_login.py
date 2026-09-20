from ui_framework.driver import ChromeDriver

from .the_internet import BASE_URL, LoginPage, SecurePage


def test_login_and_logout(driver: ChromeDriver) -> None:
    login = LoginPage(driver, BASE_URL).open()
    login.username.fill("tomsmith")
    login.password.fill("SuperSecretPassword!")
    login.submit.click()

    secure = SecurePage(driver, BASE_URL).wait_loaded()
    assert "Secure Area" in secure.heading.text
    assert "logged into a secure area" in secure.flash.banner.text.lower()

    secure.logout.click()
    login.wait_loaded()
    assert "login" in login.current_url
    assert "logged out" in login.flash.banner.text.lower()
