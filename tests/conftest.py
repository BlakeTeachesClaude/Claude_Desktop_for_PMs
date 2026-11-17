import importlib.util
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="session")
def root():
    return ROOT


@pytest.fixture()
def sync(monkeypatch):
    """Fresh import of scripts/sync.py so tests can monkeypatch its globals."""
    spec = importlib.util.spec_from_file_location("sync_under_test", ROOT / "scripts" / "sync.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod
