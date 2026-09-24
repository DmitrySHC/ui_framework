from demo.app import TheInternet


def test_toggle_checkboxes(app: TheInternet):
    app.steps.forms.checkboxes.open()
    app.asserts.forms.checkboxes.verify_states_are(False, True)

    app.steps.forms.checkboxes.set_states(True, False)
    app.asserts.forms.checkboxes.verify_states_are(True, False)
