"""Відкриті тести задачі 4: Запуск команди: fork, exec, wait.

Запуск: pytest tests/test_lab_04.py
Тут лише приклади з карток варіантів; повний набір перевірок є у викладача.
"""
import os
import signal
import sys
from pathlib import Path

import pytest
from conftest import load

PY = sys.executable
FILTERS = str(Path(__file__).resolve().parent / "filters.py")


def F(*args):
    """Команда тестової утиліти tests/filters.py (запускається інтерпретатором Python)."""
    return [PY, FILTERS, *map(str, args)]


def _ids(cases, prefix):
    return [f"{prefix}-{c[0]}-{i}" for i, c in enumerate(cases)]


@pytest.fixture(autouse=True)
def _watchdog():
    """Тест, що завис (наприклад, через незакритий кінець каналу), завершується за 20 с."""
    def boom(signum, frame):
        raise TimeoutError("тест завис довше 20 с: перевірте закриття кінців каналів і wait")
    old = signal.signal(signal.SIGALRM, boom)
    signal.alarm(20)
    yield
    signal.alarm(0)
    signal.signal(signal.SIGALRM, old)

T04 = [
    ("S1", F("exit", 0), None, 0),
    ("S1", F("exit", 3), None, 3),
    ("S1", F("exit", 255), None, 255),
    ("S2", F("kill", "SIGKILL"), None, 137),
    ("S2", F("kill", "SIGTERM"), None, 143),
    ("S2", F("kill", "SIGHUP"), None, 129),
    ("S3", ["pysh-no-such-cmd"], None, 127),
    ("S3", F("exit-env", "N"), {"N": "7"}, 7),
]


@pytest.mark.parametrize("tag,argv,env,expected", T04, ids=_ids(T04, "T04"))
def test_run_command(tag, argv, env, expected):
    M = load(4)
    assert M.run_command(argv, env) == expected



def test_no_shortcuts():
    """Заборонено готові обгортки: subprocess, os.system, os.popen, os.posix_spawn, pty."""
    import ast
    source = Path(load(4).__file__).read_text(encoding="utf-8")
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            assert not any(a.name.split(".")[0] in ("subprocess", "pty") for a in node.names), "заборонено subprocess"
        if isinstance(node, ast.ImportFrom):
            assert (node.module or "").split(".")[0] not in ("subprocess", "pty"), "заборонено subprocess"
        if isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name) and node.value.id == "os":
            assert node.attr not in ("system", "popen", "posix_spawn", "posix_spawnp"), "заборонено os.%s" % node.attr
