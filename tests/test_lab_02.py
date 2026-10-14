"""Відкриті тести задачі 2: Розбір конвеєра й перенаправлень.

Запуск: pytest tests/test_lab_02.py
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

T02 = [
    ("S1", "ls -l | wc -l", [(["ls", "-l"], None, None, False), (["wc", "-l"], None, None, False)]),
    ("S1", "echo hi>out.txt", [(["echo", "hi"], None, "out.txt", False)]),
    ("S1", "echo hi >> log", [(["echo", "hi"], None, "log", True)]),
    ("S1", "", []),
    ("S2", "sort < in.txt | uniq > out.txt", [(["sort"], "in.txt", None, False), (["uniq"], None, "out.txt", False)]),
    ("S2", 'grep "a|b" file', [(["grep", "a|b", "file"], None, None, False)]),
    ("S2", "cat file | grep x | wc -l", [(["cat", "file"], None, None, False), (["grep", "x"], None, None, False), (["wc", "-l"], None, None, False)]),
    ("S3", "ls | | wc", ValueError("Порожня команда в конвеєрі")),
    ("S3", "cat >", ValueError("Немає імені файла після перенаправлення")),
    ("S3", "echo a | cat < f", ValueError("Перенаправлення суперечить конвеєру")),
    ("S3", "| ls", ValueError("Порожня команда в конвеєрі")),
]


def _stages(spec):
    return [{"argv": a, "stdin": i, "stdout": o, "append": ap} for a, i, o, ap in spec]


@pytest.mark.parametrize("tag,line,expected", T02, ids=_ids(T02, "T02"))
def test_parse_pipeline(tag, line, expected):
    M = load(2)
    if isinstance(expected, ValueError):
        with pytest.raises(ValueError) as info:
            M.parse_pipeline(line)
        assert str(info.value) == str(expected)
    else:
        assert M.parse_pipeline(line) == _stages(expected)
