"""Відкриті тести задачі 3: Розкриття змінних і тильди.

Запуск: pytest tests/test_lab_03.py
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

ENV = {"USER": "ira", "HOME": "/home/ira", "EMPTY": ""}
T03 = [
    ("S1", "hello $USER", ENV, 0, "hello ira"),
    ("S1", "x${USER}y", ENV, 0, "xiray"),
    ("S1", "code=$?", ENV, 3, "code=3"),
    ("S1", "$NOPE", ENV, 0, ""),
    ("S2", r"cost: \$5", ENV, 0, "cost: $5"),
    ("S2", "a $ b", ENV, 0, "a $ b"),
    ("S2", "~/docs", ENV, 0, "/home/ira/docs"),
    ("S2", "~", ENV, 0, "/home/ira"),
    ("S3", "${NOPE:-guest}", ENV, 0, "guest"),
    ("S3", "${USER:-guest}", ENV, 0, "ira"),
    ("S3", "${EMPTY:-def}", ENV, 0, "def"),
    ("S3", "${NOPE", ENV, 0, ValueError("Незакрита ${")),
]


@pytest.mark.parametrize("tag,text,env,status,expected", T03, ids=_ids(T03, "T03"))
def test_expand(tag, text, env, status, expected):
    M = load(3)
    if isinstance(expected, ValueError):
        with pytest.raises(ValueError) as info:
            M.expand(text, env, status)
        assert str(info.value) == str(expected)
    else:
        assert M.expand(text, env, status) == expected


def test_status_default_is_zero():
    assert load(3).expand("$?", {}) == "0"


def test_env_is_not_modified():
    env = dict(ENV)
    load(3).expand("${NOPE:-x} $USER ~/a", env, 5)
    assert env == ENV
