# UI Framework

Фреймворк автотестирования веб-UI на **Playwright** (sync API, установленный Chrome).
Публичные контракты: `ChromeDriver(DriverConfig(...))`, фикстура `driver`, `BasePage`, `BaseElement`.

Слои: **драйвер**, **сеть** (перехват запросов), **страницы и компоненты**,
**элементы**, а поверх них — **шаги, проверки и корневой агрегатор** для тестов.

## Слой драйвера

`BaseDriver` — абстрактный класс: жизненный цикл сессии Playwright
(`Browser` → `BrowserContext` → `Page`). Параметры запуска задаются объектом
конфига `DriverConfig`, его проверяет Pydantic. Наследник объявляет
`browser_name`, `config_class` и реализует `_launch_browser(playwright)`.

`open(url)` идёт через `page.goto(wait_until=...)`, `reload()` — через
`page.reload`; чего ждать, задаёт `page_load_strategy`
(`normal` → `load`, `eager` → `domcontentloaded`, `none` → `commit`).
Консоль страницы и JS-ошибки приходят событиями `console` / `pageerror` и
пишутся в `console.log`; `driver.console_logs()` отдаёт их списком `ConsoleEntry`.

`driver.page` — нативная страница Playwright (`driver.webdriver` — тот же
объект под историческим именем). Каталогом логов владеет `DriverLogs`:
драйвер его создаёт, но не настраивает `logging`.

## Слой сети

`NetworkInterceptor` — отдельная сущность на `driver.network`. Перехват живёт
только внутри `with`: на выходе маршрут снимается (`page.unroute`).

```python
from ui_framework import BasePage, Text, url

STUB = "<!DOCTYPE html><html><body><h1 id='stubbed'>stubbed</h1></body></html>"


@url("/dropdown")
class DropdownPage(BasePage):
  heading = Text(id="stubbed")


def test_stub_dropdown(driver):
  page = DropdownPage(driver, "https://the-internet.herokuapp.com")
  with driver.network.stub("**/dropdown", body=STUB):
    page.open()
    assert page.heading.text == "stubbed"


def test_see_login_request(driver):
  with driver.network.intercept("**/login") as log:
    driver.open("https://the-internet.herokuapp.com/login")
    seen = log.wait_for("/login")
  assert seen.method == "GET"
```

`intercept(*globs)` пишет запросы в `NetworkLog` и пропускает их дальше.
`stub(*globs, body=..., status=200)` отвечает заглушкой (`route.fulfill`).
`rewrite(*globs, to=url)` забирает ответ с другого адреса и отдаёт его под
исходным URL — адресная строка не меняется. Глобы — синтаксис `page.route`:
`*`, `**`, `?`. Без шаблонов перехватываются все запросы.

## Слой страниц

`BaseInstance` хранит драйвер. От него наследуются:

- `BasePage` — страница с URL: в конструктор `(driver, base_url)`;
- `BaseComponent` — кусок UI без URL (баннер, модалка). Только `(driver,)`.
  Компонент не умеет `open` / `refresh`.

Путь страницы задаётся декоратором `@url`. Плейсхолдеры подставляются в `open` / `url`:

```python
from ui_framework import BaseComponent, BasePage, Button, Text, TextInput, url


class FlashMessage(BaseComponent):
  message = Text(css="#flash")


@url("/login/{user}")
class LoginPage(BasePage):
  username = TextInput(css="#username")
  submit = Button(css="button[type=submit]")

  def __init__(self, driver, base_url: str) -> None:
    super().__init__(driver, base_url)
    self.flash = FlashMessage(driver)


def test_login(driver):
  page = LoginPage(driver, "https://example.com")
  page.open(user="alice")
  page.username.wait_visible().fill("alice")
  page.submit.click()
```

`page.url(user="alice")` собирает абсолютный адрес без навигации. `refresh()`
перезагружает текущую вкладку, kwargs не принимает.

Элементы — дескрипторы на классе страницы или компонента. `wait_*` и `click()`
возвращают `self`. Таймаут ожидания — `ConditionNotMatchedException`.
Поиск — ровно один: `css`, `id`, `xpath`, `name`, `class_name`, `tag` либо
`role`, `by_label`, `placeholder`, `text`, `test_id`, `alt_text`, `title`.
`Button(accessible_name="Login")` и `Link(accessible_name="Docs")` берут роль
из класса. `name=` — по-прежнему HTML-атрибут.

`DriverConfig.trace`: `off` (по умолчанию), `on`, `retain-on-failure`. Фикстура
`driver` при падении пишет `failure.png`, а trace — `trace.zip` в каталог логов.
`storage_state` подставляется в контекст; `save_storage_state(path)` снимает его.
Туда же `locale`, `timezone_id`, `color_scheme`, `geolocation`, `permissions`.

## Слои тестового проекта

Поверх страниц фреймворк задаёт слои сценария и корневой агрегатор.
Рабочий пример — каталог [`demo/`](demo/README.md).

```
tests  →  app.steps.*  /  app.asserts.*
             │                 │
          StepsGroup       AssertsGroup
             │                 │
          BaseStep  ←──── BaseAssert
             │                 │
     BasePage / BaseComponent / BaseComponentSteps
                                   ↑
                          BaseComponentAsserts
```

| Слой | База | Создаётся только в | Хранит |
| --- | --- | --- | --- |
| компонент | `BaseComponent` | конструкторе страницы, шага или шага компонента | — |
| страница | `BasePage` | конструкторе шага | компоненты |
| шаг компонента | `BaseComponentSteps` | конструкторе шага, агрегатора шагов или проверки компонента | компоненты |
| шаг | `BaseStep` | конструкторе проверки или агрегатора шагов | страницы, компоненты или шаги компонентов |
| проверка компонента | `BaseComponentAsserts` | конструкторе проверки или агрегатора проверок | шаг компонента |
| проверка | `BaseAssert` | конструкторе агрегатора проверок или корневого `StepsGroup` | шаг и проверки компонентов |
| агрегаторы | `StepsGroup` / `AssertsGroup` | родительском агрегаторе или на верхнем уровне | шаги/проверки, шаги/проверки компонентов и под-агрегаторы |
| корневой агрегатор | `StepsGroup` | верхнем уровне (фикстура) | `steps`, `asserts` и любые объекты без слоя |

```python
class FlashComponentSteps(BaseComponentSteps):
    def __init__(self, driver, base_url):
        super().__init__(driver, base_url)
        self.flash = FlashMessage(driver)

    def dismiss(self):
        self.flash.close()
        return self

    @readonly
    def text(self) -> str:
        return self.flash.message()


class FlashComponentAsserts(BaseComponentAsserts):
    def __init__(self, driver, base_url):
        super().__init__(driver, base_url)
        self.step = FlashComponentSteps(driver, base_url)

    def contains(self, text):
        flash = self.step.text()
        assert text.lower() in flash.lower()
        return self


class AuthSteps(BaseStep):
    def __init__(self, driver, base_url):
        super().__init__(driver, base_url)
        self.login = LoginPage(driver, base_url)
        self.secure = SecurePage(driver, base_url)
        self.flash = FlashComponentSteps(driver, base_url)

    def login_as(self, user, password):
        self.login.open().sign_in(user, password)
        return self

    @readonly
    def secure_heading(self) -> str:
        return self.secure.wait_loaded().heading_text()


class AuthAsserts(BaseAssert):
    def __init__(self, driver, base_url):
        super().__init__(driver, base_url)
        self.step = AuthSteps(driver, base_url)
        self.flash = FlashComponentAsserts(driver, base_url)

    def logged_in(self):
        assert "Secure Area" in self.step.secure_heading()
        return self


class TheInternet(StepsGroup):
    def __init__(self, driver, base_url):
        super().__init__(driver, base_url)
        self.steps = Steps(driver, base_url)
        self.asserts = Asserts(driver, base_url)


def test_login(app):
    app.steps.auth.login_as("tomsmith", "SuperSecretPassword!")
    app.asserts.auth.verify_logged_in()
    app.asserts.auth.flash.verify_contains("logged into a secure area")
```

Правила проверяются в рантайме и поднимают `LayerError`:

- место создания: компонент вне конструктора страницы, шага или шага компонента;
  шаг компонента вне шага / агрегатора шагов / проверки компонента; страница вне
  конструктора шага; шаг вне проверки/агрегатора; проверка и проверка компонента
  вне агрегатора проверок (проверка — ещё и вне корневого агрегатора шагов);
- состав: шаг хранит страницы, компоненты или шаги компонентов; проверка — шаг и
  проверки компонентов; шаг компонента — только компоненты; проверка компонента —
  только шаг компонента; вложенный агрегатор — только своих детей; корневой
  `StepsGroup` — шаги, проверки и объекты без слоя;
- элементы и драйвер: у страницы или компонента, созданных под шагом, `driver` (а через него —
  все элементы и сырой `Page`) доступен только методам страниц и компонентов —
  `self.page.username.fill(...)` или `self.page.driver` из шага поднимают `LayerError`;
- asserts не меняют состояние: из проверки доступны только методы шага с
  `@readonly`; клик, `fill`, `check`, `select_*`, `open`, `refresh` внутри вызова
  проверки поднимают `LayerError`, даже если спрятаны за `@readonly`;
- `AssertionError` внутри шага, страницы или компонента превращается в `LayerError`.

Что рантайм не видит, проверяет статический анализ `ui_framework.layers.check_project(root)`:
классы слоёв лежат в `pages/`, `steps/`, `asserts/`, корневой `StepsGroup` — в корне
или в `steps/`; `assert` и `AssertionError` только в `asserts/`; виджеты
импортируются только в `pages/`; `.driver` и `.web_element` вне `pages/` не
встречаются; конструкторы вызываются в нужных `__init__`; тесты не импортируют
слои и работают только через корневой агрегатор. `ensure_architecture(root)` поднимает
`ArchitectureError` со списком — удобно вызывать из теста без `assert`.

Страницы, созданные напрямую в тесте (как в `tests/` самого фреймворка),
правилам слоёв не подчиняются: они нужны для юнит-тестов виджетов.

## Pytest

В `conftest.py` набора тестов:

```python
pytest_plugins = ("ui_framework.fixtures.driver",)
```

Фикстуры: `webdriver_settings` → `webdriver_config` → `driver`.
Драйвер стартует перед тестом и вызывает `quit()` после.

Проверки пишутся через `assert_that` и матчеры Hamcrest (`equal_to`, `contains_string`, `ends_with` и остальные из `ui_framework`). Методы проверок начинаются с `verify_`. `assert_that` разрешён только в `asserts/`.

При падении теста фикстура прикладывает к Allure скриншот, `session.log`, `console.log` и `trace.zip`, если они есть. Отчёт собирается так:

```powershell
uv run pytest --alluredir=allure-results
allure generate allure-results -o allure-report
```

```python
def test_login(driver):
    driver.open("https://the-internet.herokuapp.com/login")
    assert "Login" in driver.page.title()
```

Базовые настройки — переопределите `webdriver_settings` (ключи = поля `DriverConfig`):

```python
# tests/conftest.py
import pytest

pytest_plugins = ("ui_framework.fixtures.driver",)


@pytest.fixture
def webdriver_settings():
    return {"is_headless": True, "is_incognito": True}
```

Для одного теста или класса:

```python
class TestMobile:
    @pytest.fixture
    def webdriver_settings(self):
        return {"is_headless": True, "is_mobile": True}

    def test_viewport(self, driver):
        ...
```

Или parametrize:

```python
@pytest.mark.parametrize(
    "webdriver_settings",
    [{"is_headless": True}, {"is_headless": True, "is_mobile": True}],
    indirect=True,
)
def test_modes(driver, webdriver_config):
    ...
```

Можно вернуть готовый `DriverConfig` из `webdriver_settings` — фикстура конфига пропустит его как есть.

### Использование без pytest

```python
from ui_framework import ChromeDriver, DriverConfig

driver = ChromeDriver(DriverConfig(is_headless=True, window_size=(1280, 720)))
driver.start()
driver.open("https://the-internet.herokuapp.com/login")
print(driver.page.title())
driver.quit()
```

Мобильная эмуляция: `is_mobile=True` берёт устройство по умолчанию (`Pixel 5`),
конкретное указывается через `device`.

```python
driver = ChromeDriver(DriverConfig(is_headless=True, is_mobile=True, device="iPhone 12 Pro"))
```

### Параметры `DriverConfig`

| Параметр | Тип | По умолчанию | Назначение |
| --- | --- | --- | --- |
| `is_headless` | `bool` | `False` | Запуск без окна |
| `is_mobile` | `bool` | `False` | Мобильная эмуляция: viewport, DPR, User-Agent, touch |
| `is_incognito` | `bool` | `False` | Сохранён для совместимости: каждый `BrowserContext` Playwright и так изолирован |
| `device` | `str \| None` | `None` | Пресет устройства; требует `is_mobile=True` |
| `window_size` | `tuple[int, int]` | `(1600, 1000)` | Viewport; игнорируется в мобильном режиме |
| `browser_args` | `tuple[str, ...]` | `()` | Дополнительные аргументы Chrome (непустые строки) |
| `logs_dir` | `Path` | `logs` | Корень каталогов с логами |
| `downloads_dir` | `Path` | `downloads` | Каталог загрузок |
| `page_load_timeout` | `float` | `60.0` | Таймаут навигации, секунды |
| `script_timeout` | `float` | `30.0` | Таймаут остальных действий Playwright, секунды |
| `page_load_strategy` | `normal` / `eager` / `none` | `normal` | Чего ждёт `open()`: `load` / `domcontentloaded` / `commit` |

Chrome всегда получает `--no-sandbox`, `--disable-dev-shm-usage`, `--disable-gpu`.
Неявных ожиданий нет: элементы ждут только явными `wait_*`.

Пресеты устройств (`DEVICE_PROFILES`): `Pixel 5` (по умолчанию), `iPhone 12 Pro`,
`Galaxy S20`. Метрики и User-Agent заданы явно и уходят в `Browser.new_context(...)`.

Ошибки валидации поднимают `DriverConfigurationError`:

```
is_headless: Input should be a valid boolean
device: Extra inputs are not permitted          # опечатка в имени поля
device='Pixel 5' передан без is_mobile=True
```

### Логи

Каждый запуск получает отдельный каталог `logs/<browser>-<дата>-<pid>-<n>/`
(путь абсолютный: процесс браузера стартует со своим рабочим каталогом).
В нём три файла с разными источниками:

| Файл | Что внутри |
| --- | --- |
| `browser.log` | лог процесса Chrome (`--enable-logging --v=1`) |
| `console.log` | консоль страницы и JS-ошибки (события Playwright, пишутся сразу) |
| `session.log` | события драйвера: параметры, старт и остановка сессии |

Каталог создаётся при конструировании объекта, поэтому логи остаются на диске,
даже если браузер так и не поднялся — причина обычно лежит в `browser.log`.

## Окружение

Пакетный менеджер — [uv](https://docs.astral.sh/uv/). Python 3.12, установленный
Chrome (Playwright берёт его через `channel="chrome"`, скачивать браузер не нужно).

```powershell
uv sync                          # окружение из uv.lock + editable-установка пакета
uv run ruff check src demo tests
uv run mypy src demo tests       # strict
uv run pytest                    # тесты фреймворка (живой Chrome)
uv run pytest demo               # демо-проект по шаблону слоёв
```
