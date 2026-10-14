import sys
import pytest
from conftest import load

M = load(8)  # Завантажуємо модуль задачі 8

@pytest.mark.parametrize("args, expected", [
    ([sys.executable, "tests/filters.py", "exit", "0"], 0),
    ([sys.executable, "tests/filters.py", "exit", "7"], 7),
    ([sys.executable, "tests/filters.py", "kill", "SIGTERM"], 143),
])
def test_my_cases(args, expected):
    assert M.run_foreground(args) == expected