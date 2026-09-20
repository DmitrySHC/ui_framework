from pathlib import Path

from ui_framework import (
    BasePage,
    Button,
    Checkbox,
    Image,
    Link,
    RadioButton,
    Select,
    Text,
    TextInput,
    url,
)

SAMPLE_HTML = Path(__file__).with_name("sample.html")


@url(SAMPLE_HTML.as_uri())
class SamplePage(BasePage):
    heading = Text(id="heading")
    status = Text(id="status")
    docs = Link(id="docs")
    username = TextInput(id="username")
    agree = Checkbox(id="agree")
    color_red = RadioButton(id="color-red")
    color_blue = RadioButton(id="color-blue")
    country = Select(id="country")
    logo = Image(id="logo")
    submit = Button(id="submit")
    frozen = Button(id="frozen")
    secret = Text(id="secret")
    missing = Text(id="missing", label="Missing")
