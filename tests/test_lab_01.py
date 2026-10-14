"""Відкриті тести задачі 1: Розбір командного рядка на слова.

Запуск: pytest tests/test_lab_01.py
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

T01 = [
    ("S1", "ls -l /tmp", ["ls", "-l", "/tmp"]),
    ("S1", "  echo   a   b  ", ["echo", "a", "b"]),
    ("S1", "", []),
    ("S2", 'echo "hello world"', ["echo", "hello world"]),
    ("S2", "echo 'a  b' c", ["echo", "a  b", "c"]),
    ("S2", 'echo ab"c d"e', ["echo", "abc de"]),
    ("S2", 'echo ""', ["echo", ""]),
    ("S3", r"echo a\ b", ["echo", "a b"]),
    ("S3", r'echo "say \"hi\""', ["echo", 'say "hi"']),
    ("S3", "echo x # note", ["echo", "x"]),
    ("S3", "echo 'abc", ValueError("Незакрита лапка")),
]


@pytest.mark.parametrize("tag,line,expected", T01, ids=_ids(T01, "T01"))
def test_tokenize(tag, line, expected):
    M = load(1)
    if isinstance(expected, ValueError):
        with pytest.raises(ValueError) as info:
            M.tokenize(line)
        assert str(info.value) == str(expected)
    else:
        assert M.tokenize(line) == expected
