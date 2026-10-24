import json
import sys
from pathlib import Path

import pytest
from click.testing import CliRunner

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from devhive_cli import main as devhive_main


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def isolated_home(tmp_path, monkeypatch):
    home = tmp_path / "home"
    home.mkdir()
    monkeypatch.setattr(devhive_main.Path, "home", classmethod(lambda cls: home))
    monkeypatch.setattr(devhive_main, "OPENCODE_CONFIG_DIR", home / ".config" / "opencode")
    monkeypatch.setattr(devhive_main, "TARGET_DIR", home / ".config" / "opencode" / "skills")
    monkeypatch.setattr(devhive_main, "TARGET_AGENTS_DIR", home / ".config" / "opencode" / "agents")
    monkeypatch.setattr(devhive_main, "TARGET_PLUGINS_DIR", home / ".config" / "opencode" / "plugins")
    monkeypatch.setattr(devhive_main, "TARGET_CONFIG_FILE", home / ".config" / "opencode" / "opencode.json")
    return home


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))
