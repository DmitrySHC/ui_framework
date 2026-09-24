from demo.app import TheInternet


def test_person_row(app: TheInternet):
    app.steps.tables.open()
    app.asserts.tables.verify_heading_is("Data Tables").verify_smith_email_is("jsmith@gmail.com")
    app.asserts.tables.verify_doe_due_is("$100.00")

    app.steps.tables.delete_smith()
    app.asserts.tables.verify_at_delete()
