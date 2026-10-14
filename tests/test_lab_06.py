"""Відкриті тести задачі 6: Перенаправлення вводу-виводу.

Запуск: pytest tests/test_lab_06.py
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

T06 = [
    ("S1", F("words", "x", "y"), None, "out.txt", None, False, "x\ny\n", 0),
    ("S1", F("words", "new"), None, "out.txt", "old content\n", False, "new\n", 0),
    ("S1", F("gen", 3), None, "out.txt", None, False, "0\n1\n2\n", 0),
    ("S2", F("words", "b"), None, "out.txt", "a\n", True, "a\nb\n", 0),
    ("S2", F("words", "first"), None, "out.txt", None, True, "first\n", 0),
    ("S2", F("upper"), "hello\n", "out.txt", None, False, "HELLO\n", 0),
    ("S3", F("rev"), "1\n2\n", "out.txt", None, False, "2\n1\n", 0),
    ("S3", F("cat"), False, "out.txt", None, False, None, 1),
    ("S3", F("words", "x"), None, "no_dir/out.txt", None, False, None, 1),
]


@pytest.mark.parametrize("tag,argv,stdin_text,out_name,pre_out,append,expected_out,expected_status", T06,
                         ids=_ids(T06, "T06"))
def test_run_redirected(tag, argv, stdin_text, out_name, pre_out, append, expected_out, expected_status, tmp_path):
    M = load(6)
    stdin_path = None
    if stdin_text is False:
        stdin_path = str(tmp_path / "missing_in.txt")
    elif stdin_text is not None:
        (tmp_path / "in.txt").write_text(stdin_text, encoding="utf-8")
        stdin_path = str(tmp_path / "in.txt")
    out_path = str(tmp_path / out_name)
    if pre_out is not None:
        Path(out_path).write_text(pre_out, encoding="utf-8")
    assert M.run_redirected(argv, stdin_path, out_path, append) == expected_status
    if expected_out is None:
        assert not os.path.exists(out_path)
    else:
        assert Path(out_path).read_text(encoding="utf-8") == expected_out



def test_no_shortcuts():
    """Заборонено готові обгортки: subprocess, os.system, os.popen, os.posix_spawn, pty."""
    import ast
    source = Path(load(6).__file__).read_text(encoding="utf-8")
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            assert not any(a.name.split(".")[0] in ("subprocess", "pty") for a in node.names), "заборонено subprocess"
        if isinstance(node, ast.ImportFrom):
            assert (node.module or "").split(".")[0] not in ("subprocess", "pty"), "заборонено subprocess"
        if isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name) and node.value.id == "os":
            assert node.attr not in ("system", "popen", "posix_spawn", "posix_spawnp"), "заборонено os.%s" % node.attr
