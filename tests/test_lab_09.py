"""Відкриті тести задачі 9: Списки команд: ; && ||.

Запуск: pytest tests/test_lab_09.py
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

T09 = [
    ("S1", "a ; b ; c", ["a", "b", "c"], 0),
    ("S1", "a;b", ["a", "b"], 0),
    ("S1", "fail ; b", ["fail", "b"], 0),
    ("S1", "a ; fail", ["a", "fail"], 1),
    ("S2", "a && b", ["a", "b"], 0),
    ("S2", "fail && b", ["fail"], 1),
    ("S2", "fail || b", ["fail", "b"], 0),
    ("S2", "a || b", ["a"], 0),
    ("S3", 'echo "a && b"', ['echo "a && b"'], 0),
    ("S3", "a ; fail && b ; c", ["a", "fail", "c"], 0),
    ("S3", "a &&", [], ValueError("Порожня команда")),
    ("S3", "; a", [], ValueError("Порожня команда")),
]


def _runner(calls):
    def run(command):
        calls.append(command)
        words = command.split()
        return {"fail": 1, "two": 2}.get(words[0] if words else "", 0)
    return run


@pytest.mark.parametrize("tag,line,expected_calls,expected", T09, ids=_ids(T09, "T09"))
def test_run_list(tag, line, expected_calls, expected):
    M = load(9)
    calls = []
    if isinstance(expected, ValueError):
        with pytest.raises(ValueError) as info:
            M.run_list(line, _runner(calls))
        assert str(info.value) == str(expected)
        assert calls == [], "помилку синтаксису треба виявити до виконання будь-якої команди"
    else:
        assert M.run_list(line, _runner(calls)) == expected
        assert calls == expected_calls
