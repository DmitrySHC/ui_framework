from demo.app import TheInternet


def test_choose_option(app: TheInternet) -> None:
    app.steps.forms.dropdown.choose("Option 2")
    app.asserts.forms.dropdown.heading_is("Dropdown List").selected_is("Option 2")
