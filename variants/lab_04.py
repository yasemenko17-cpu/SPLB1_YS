"""Лабораторна SP-LAB01. Задача 4: Запуск команди: fork, exec, wait.

Правила — у student.md (розділ 7, задача 4) та в картці вашого варіанта.
Відкриті тести: pytest tests/test_lab_04.py
"""
import os
import sys


def run_command(argv: list[str], env: dict | None = None) -> int:
    """Запускає команду (fork, exec, wait) і повертає код завершення."""
    raise NotImplementedError  # TODO: реалізуйте за описом задачі
