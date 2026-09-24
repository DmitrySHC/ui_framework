from demo.app import TheInternet


def test_choose_option(app: TheInternet):
    app.steps.forms.dropdown.choose("Option 2")
    app.asserts.forms.dropdown.verify_heading_is("Dropdown List").verify_selected_is("Option 2")
