"""Відкриті тести задачі 7: Внутрішні команди оболонки.

Запуск: pytest tests/test_lab_07.py
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

T07 = [
    ("S1", {}, [dict(argv=["pwd"], out="{tmp}\n", status=0), dict(argv=["cd", "sub"], out="", status=0, cwd="{tmp}/sub", pwd="{tmp}/sub"), dict(argv=["pwd"], out="{tmp}/sub\n"), dict(argv=["cd", "deep"], cwd="{tmp}/sub/deep", pwd="{tmp}/sub/deep"), dict(argv=["cd", ".."], cwd="{tmp}/sub")]),
    ("S2", {}, [dict(argv=["cd"], cwd="{tmp}/home", pwd="{tmp}/home", status=0), dict(argv=["cd", "../sub"], cwd="{tmp}/sub"), dict(argv=["cd", "-"], out="{tmp}/home\n", cwd="{tmp}/home"), dict(argv=["cd", "nope"], status=1, err="cd: nope: Немає такого каталогу", cwd="{tmp}/home")]),
    ("S3", {}, [dict(argv=["export", "A=1"], env={"A": "1"}, status=0), dict(argv=["export", "B=two words"], env={"B": "two words"}), dict(argv=["unset", "A"], noenv=["A"], status=0), dict(argv=["ls", "-l"], ret=False, status=0, exit=None), dict(argv=["exit", "7"], exit=7)]),
]


def _fill(value, root):
    if isinstance(value, str):
        return value.replace("{tmp}", str(root))
    if isinstance(value, dict):
        return {k: _fill(v, root) for k, v in value.items()}
    if isinstance(value, list):
        return [_fill(v, root) for v in value]
    return value


@pytest.mark.parametrize("tag,init,steps", T07, ids=_ids(T07, "T07"))
def test_builtins(tag, init, steps, tmp_path, monkeypatch, capfd):
    M = load(7)
    root = tmp_path.resolve()
    for name in ("home", "sub/deep", "other"):
        (root / name).mkdir(parents=True)
    (root / "file.txt").write_text("x")
    monkeypatch.chdir(root)
    state = {"env": {"HOME": str(root / "home"), "PWD": str(root)}, "status": 0, "exit": None, "oldpwd": None}
    state.update(_fill(init, root))
    for number, step in enumerate(_fill(steps, root), 1):
        where = f"крок {number}: {step['argv']}"
        returned = M.run_builtin(list(step["argv"]), state)
        out, err = capfd.readouterr()
        assert returned is step.get("ret", True), where + ": неправильне значення, що повертається"
        if "status" in step:
            assert state["status"] == step["status"], where + ": state['status']"
        if "out" in step:
            assert out == step["out"], where + ": stdout"
        if "err" in step:
            assert step["err"] in err, where + ": stderr"
        if "cwd" in step:
            assert os.getcwd() == step["cwd"], where + ": поточний каталог"
        if "pwd" in step:
            assert state["env"].get("PWD") == step["pwd"], where + ": PWD"
        if "exit" in step:
            assert state["exit"] == step["exit"], where + ": state['exit']"
        for key, value in step.get("env", {}).items():
            assert state["env"].get(key) == value, where + f": змінна {key}"
        for key in step.get("noenv", []):
            assert key not in state["env"], where + f": змінна {key} має бути видалена"
