import subprocess
import sys
from pathlib import Path


def _run(root: Path, body: str) -> None:
    (root / "conftest.py").write_text(
        "from pathlib import Path\n"
        "import pytest\n"
        "pytest_plugins = ('ui_framework.fixtures.driver',)\n"
        "\n"
        f"LOGS = Path({str(root / 'logs')!r})\n"
        "\n"
        "@pytest.fixture\n"
        "def webdriver_settings():\n"
        "    return {'logs_dir': LOGS, 'is_headless': True}\n",
        encoding="utf-8",
    )
    (root / "test_phase.py").write_text(body, encoding="utf-8")
    completed = subprocess.run(
        [sys.executable, "-m", "pytest", "-p", "no:cacheprovider", str(root), "-q"],
        cwd=root,
        capture_output=True,
        text=True,
        check=False,
    )
    shots = list(root.rglob("failure.png"))
    assert shots, completed.stdout + completed.stderr
    assert completed.returncode != 0


def test_screenshot_when_the_test_fails(tmp_path: Path):
    _run(
        tmp_path,
        "def test_call(driver):\n"
        "    driver.open('about:blank')\n"
        "    raise AssertionError('call failed')\n",
    )


def test_screenshot_when_setup_fails(tmp_path: Path):
    _run(
        tmp_path,
        "import pytest\n"
        "\n"
        "@pytest.fixture\n"
        "def broken_setup(driver):\n"
        "    driver.open('about:blank')\n"
        "    raise RuntimeError('setup failed')\n"
        "\n"
        "def test_setup(broken_setup):\n"
        "    pass\n",
    )


def test_screenshot_when_teardown_fails(tmp_path: Path):
    _run(
        tmp_path,
        "import pytest\n"
        "\n"
        "@pytest.fixture\n"
        "def broken_teardown(driver):\n"
        "    driver.open('about:blank')\n"
        "    yield\n"
        "    raise RuntimeError('teardown failed')\n"
        "\n"
        "def test_teardown(broken_teardown):\n"
        "    pass\n",
    )
