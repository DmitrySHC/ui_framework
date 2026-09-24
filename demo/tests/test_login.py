from demo.app import TheInternet


def test_login_and_logout(app: TheInternet):
    app.steps.auth.login_as("tomsmith", "SuperSecretPassword!")
    app.asserts.auth.logged_in()
    app.asserts.auth.flash.contains("logged into a secure area")

    app.steps.auth.logout()
    app.asserts.auth.logged_out()
    app.asserts.auth.flash.contains("logged out")


def test_wrong_password_stays_on_login(app: TheInternet):
    app.steps.auth.login_as("tomsmith", "wrong")
    app.asserts.auth.logged_out()
    app.asserts.auth.flash.contains("password is invalid")
    app.steps.auth.flash.dismiss()
    app.asserts.auth.flash.is_absent()
