"""Лабораторна SP-LAB01. Задача 10: Пошук виконуваних файлів у PATH.

Правила — у student.md (розділ 7, задача 10) та в картці вашого варіанта.
Відкриті тести: pytest tests/test_lab_10.py
"""
import os


def find_executable(name: str, path_env: str, cwd: str | None = None) -> str | None:
    """Шукає виконуваний файл за іменем (PATH або явний шлях)."""
    raise NotImplementedError  # TODO: реалізуйте за описом задачі


def complete_command(prefix: str, path_env: str) -> list[str]:
    """Повертає відсортований список імен команд, що починаються з prefix."""
    raise NotImplementedError  # TODO: реалізуйте за описом задачі
