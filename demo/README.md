# Демо: слои tests → steps / asserts → pages + components

Тестовый проект на [the-internet.herokuapp.com](https://the-internet.herokuapp.com),
собранный по шаблону слоёв `ui_framework`.

```
demo/
  app.py                 TheInternet(StepsGroup) — корневой агрегатор: steps, asserts
  conftest.py            фикстуры driver и app
  pages/                 страницы и компоненты — единственное место работы с элементами
    components/            компоненты, общие для нескольких страниц
      flash.py           FlashMessage: баннер #flash на login и secure
    login.py             LoginPage: в конструкторе создаёт FlashMessage
    secure.py            SecurePage
    dropdown.py          DropdownPage
    checkboxes.py        CheckboxesPage
    elements/
      person_row.py      PersonRow(BaseElement)
    tables.py            TablesPage
  steps/                 действия; шаг хранит страницы, компоненты или шаги компонентов
    components/
      flash.py           FlashComponentSteps: держит FlashMessage
    auth.py              AuthSteps: LoginPage + SecurePage + FlashComponentSteps
    dropdown.py          DropdownSteps
    checkboxes.py        CheckboxesSteps
    forms.py             FormsSteps(StepsGroup) — под-агрегатор
    tables.py            TablesSteps
    __init__.py          Steps(StepsGroup): auth, forms, tables
  asserts/               проверки; каждая создаёт шаг своего домена
    components/
      flash.py           FlashComponentAsserts → FlashComponentSteps
    auth.py              AuthAsserts → AuthSteps + FlashComponentAsserts
    dropdown.py          DropdownAsserts → DropdownSteps
    checkboxes.py        CheckboxesAsserts → CheckboxesSteps
    forms.py             FormsAsserts(AssertsGroup)
    tables.py            TablesAsserts → TablesSteps
    __init__.py          Asserts(AssertsGroup): auth, forms, tables
  tests/                 только app.steps.* и app.asserts.*
    test_login.py
    test_dropdown.py
    test_checkboxes.py
    test_tables.py
    test_architecture.py статическая проверка слоёв всего каталога demo/
```

Тест видит только корневой агрегатор:

```python
def test_login_and_logout(app: TheInternet):
    app.steps.auth.login_as("tomsmith", "SuperSecretPassword!")
    app.asserts.auth.logged_in()
    app.asserts.auth.flash.contains("logged into a secure area")

    app.steps.auth.logout()
    app.asserts.auth.logged_out()
    app.asserts.auth.flash.contains("logged out")
```

Иерархия агрегаторов: `app.steps.forms.dropdown.choose("Option 2")` и
зеркальная `app.asserts.forms.dropdown.selected_is("Option 2")`.
Баннер входит в сценарий, которому он нужен: `app.steps.auth.flash` /
`app.asserts.auth.flash`. Если фрагмент появится у форм — тот же
`FlashComponentSteps` создают в конструкторе `FormsSteps`.

## Запуск

Из корня `ui_framework` (тесты ходят на живой the-internet.herokuapp.com,
нужен доступ в интернет и установленный Chrome):

```powershell
uv run pytest demo
```

`test_architecture.py` вызывает `ensure_architecture(demo/)`: нарушение
раскладки, `assert` вне `asserts/`, виджет вне `pages/` или страница, созданная
вне конструктора шага, падают с `ArchitectureError` и списком мест.

## Что ловится в рантайме

- `AuthSteps.__init__` создаёт `LoginPage` и `FlashComponentSteps` — можно;
  `LoginPage` внутри метода шага — `LayerError`.
- `self.login.username` из шага — `LayerError`: элементы доступны только методам
  страницы и её компонентов.
- `app.asserts.auth` может звать только `@readonly`-методы `AuthSteps`;
  `login_as` из проверки — `LayerError`. То же для `app.asserts.auth.flash`.
- `AssertionError` внутри страницы или шага — `LayerError`.
