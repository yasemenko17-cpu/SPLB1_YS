"""Відкриті тести задачі 5: Конвеєр із pipe.

Запуск: pytest tests/test_lab_05.py
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

T05 = [
    ("S1", [F("words", "pear", "apple", "fig"), F("sort")], "apple\nfig\npear\n", [0, 0]),
    ("S1", [F("words", "a", "b"), F("upper")], "A\nB\n", [0, 0]),
    ("S1", [F("gen", 5), F("count")], "5\n", [0, 0]),
    ("S2", [F("words", "pear", "apple", "fig"), F("sort"), F("upper")], "APPLE\nFIG\nPEAR\n", [0, 0, 0]),
    ("S2", [F("gen", 12), F("head", 3), F("count")], "3\n", [0, 0, 0]),
    ("S2", [F("words", "b", "a"), F("sort"), F("rev"), F("upper")], "B\nA\n", [0, 0, 0, 0]),
    ("S3", [F("words", "a")], "a\n", [0]),
    ("S3", [F("words", "a", "b"), F("fail", 3), F("count")], "0\n", [0, 3, 0]),
    ("S3", [["pysh-no-such-cmd"], F("count")], "0\n", [127, 0]),
]


@pytest.mark.parametrize("tag,stages,expected_out,expected_codes", T05, ids=_ids(T05, "T05"))
def test_run_pipeline(tag, stages, expected_out, expected_codes, tmp_path):
    M = load(5)
    out = tmp_path / "out.txt"
    codes = M.run_pipeline(stages, str(out))
    assert codes == expected_codes
    assert out.read_text(encoding="utf-8") == expected_out



def test_no_shortcuts():
    """Заборонено готові обгортки: subprocess, os.system, os.popen, os.posix_spawn, pty."""
    import ast
    source = Path(load(5).__file__).read_text(encoding="utf-8")
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            assert not any(a.name.split(".")[0] in ("subprocess", "pty") for a in node.names), "заборонено subprocess"
        if isinstance(node, ast.ImportFrom):
            assert (node.module or "").split(".")[0] not in ("subprocess", "pty"), "заборонено subprocess"
        if isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name) and node.value.id == "os":
            assert node.attr not in ("system", "popen", "posix_spawn", "posix_spawnp"), "заборонено os.%s" % node.attr
