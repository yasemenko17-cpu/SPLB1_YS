"""Лабораторна SP-LAB01. Задача 7: Внутрішні команди оболонки.

Правила — у student.md (розділ 7, задача 7) та в картці вашого варіанта.
Відкриті тести: pytest tests/test_lab_07.py
"""
import os
import sys


def run_builtin(argv: list[str], state: dict) -> bool:
    """Виконує внутрішню команду (cd, pwd, exit, export, unset); True, якщо команда внутрішня."""
    raise NotImplementedError  # TODO: реалізуйте за описом задачі
