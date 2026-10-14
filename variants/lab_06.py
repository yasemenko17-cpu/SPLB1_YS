"""Лабораторна SP-LAB01. Задача 6: Перенаправлення вводу-виводу.

Правила — у student.md (розділ 7, задача 6) та в картці вашого варіанта.
Відкриті тести: pytest tests/test_lab_06.py
"""
import os
import sys


def run_redirected(argv: list[str], stdin_path: str | None = None, stdout_path: str | None = None, append: bool = False) -> int:
    """Запускає команду з перенаправленнями < > >> і повертає код завершення."""
    raise NotImplementedError  # TODO: реалізуйте за описом задачі
