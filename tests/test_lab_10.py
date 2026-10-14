"""Відкриті тести задачі 10: Пошук виконуваних файлів у PATH.

Запуск: pytest tests/test_lab_10.py
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

T10 = [
    ("S1", "find", {"bin/ls": "x"}, "{tmp}/bin", "ls", None, "{tmp}/bin/ls"),
    ("S1", "find", {"bin/ls": "x"}, "{tmp}/bin", "cat", None, None),
    ("S1", "find", {"b1/ls": "x", "b2/ls": "x"}, "{tmp}/b1:{tmp}/b2", "ls", None, "{tmp}/b1/ls"),
    ("S2", "find", {"b1/tool": "f", "b2/tool": "x"}, "{tmp}/b1:{tmp}/b2", "tool", None, "{tmp}/b2/tool"),
    ("S2", "find", {"b1/sub": "d", "b2/sub": "x"}, "{tmp}/b1:{tmp}/b2", "sub", None, "{tmp}/b2/sub"),
    ("S2", "find", {"b/ls": "x"}, "{tmp}/missing::{tmp}/b", "ls", None, "{tmp}/b/ls"),
    ("S3", "find", {"w/tool": "x"}, "", "./tool", "{tmp}/w", "./tool"),
    ("S3", "find", {"w/tool": "f"}, "", "./tool", "{tmp}/w", None),
    ("S3", "complete", {"b1/git": "x", "b1/gzip": "x", "b2/grep": "x", "b2/go": "f", "b2/ls": "x"}, "{tmp}/b1:{tmp}/b2", "g", None, ["git", "grep", "gzip"]),
]


def _build(root, files):
    for rel, kind in files.items():
        path = root / rel
        if kind == "d":
            path.mkdir(parents=True, exist_ok=True)
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("#!/bin/sh\n")
            path.chmod(0o755 if kind == "x" else 0o644)


@pytest.mark.parametrize("tag,call,files,path_env,arg,cwd,expected", T10, ids=_ids(T10, "T10"))
def test_path_search(tag, call, files, path_env, arg, cwd, expected, tmp_path):
    M = load(10)
    root = tmp_path.resolve()
    _build(root, files)
    path_env = path_env.replace("{tmp}", str(root))
    arg = arg.replace("{tmp}", str(root))
    if call == "find":
        args = (arg, path_env) if cwd is None else (arg, path_env, cwd.replace("{tmp}", str(root)))
        result = M.find_executable(*args)
        assert result == (expected.replace("{tmp}", str(root)) if expected else None)
    else:
        assert M.complete_command(arg, path_env) == expected
