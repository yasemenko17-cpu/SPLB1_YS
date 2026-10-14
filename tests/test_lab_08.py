"""Відкриті тести задачі 8: SIGINT і завдання на передньому плані.

Запуск: pytest tests/test_lab_08.py
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

T08 = [
    ("S1", F("exit", 0), 0),
    ("S1", F("exit", 4), 4),
    ("S1", F("kill", "SIGINT"), 130),
    ("S2", F("inherit-check"), 0),
    ("S2", F("signal-parent", "SIGINT"), 0),
    ("S3", ["pysh-no-such-cmd"], 127),
    ("S3", F("sleep", "0.2"), 0),
    ("S3", F("kill", "SIGTERM"), 143),
]


@pytest.mark.parametrize("tag,argv,expected", T08, ids=_ids(T08, "T08"))
def test_run_foreground(tag, argv, expected):
    M = load(8)
    caught = []

    def recorder(signum, frame):
        caught.append(signum)

    old = signal.signal(signal.SIGINT, recorder)
    try:
        assert M.run_foreground(argv) == expected
        assert signal.getsignal(signal.SIGINT) is recorder, "після завершення дитини треба відновити попередній обробник SIGINT"
    finally:
        signal.signal(signal.SIGINT, old)
    assert caught == [], "поки оболонка чекає на дитину, SIGINT має ігноруватися"



def test_no_shortcuts():
    """Заборонено готові обгортки: subprocess, os.system, os.popen, os.posix_spawn, pty."""
    import ast
    source = Path(load(8).__file__).read_text(encoding="utf-8")
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            assert not any(a.name.split(".")[0] in ("subprocess", "pty") for a in node.names), "заборонено subprocess"
        if isinstance(node, ast.ImportFrom):
            assert (node.module or "").split(".")[0] not in ("subprocess", "pty"), "заборонено subprocess"
        if isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name) and node.value.id == "os":
            assert node.attr not in ("system", "popen", "posix_spawn", "posix_spawnp"), "заборонено os.%s" % node.attr
