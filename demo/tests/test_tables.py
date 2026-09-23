from demo.app import TheInternet


def test_person_row(app: TheInternet):
    app.steps.tables.open()
    app.asserts.tables.heading_is("Data Tables").smith_email_is("jsmith@gmail.com").doe_due_is("$100.00")

    app.steps.tables.delete_smith()
    app.asserts.tables.at_delete()
