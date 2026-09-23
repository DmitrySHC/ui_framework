from demo.app import TheInternet


def test_login_and_logout(app: TheInternet):
    app.steps.auth.login_as("tomsmith", "SuperSecretPassword!")
    app.asserts.auth.logged_in().flash_contains("logged into a secure area")

    app.steps.auth.logout()
    app.asserts.auth.logged_out().flash_contains("logged out")


def test_wrong_password_stays_on_login(app: TheInternet):
    app.steps.auth.login_as("tomsmith", "wrong")
    app.asserts.auth.logged_out().flash_contains("password is invalid")
