"""Лабораторна SP-LAB01. Задача 8: SIGINT і завдання на передньому плані.

Правила — у student.md (розділ 7, задача 8) та в картці вашого варіанта.
Відкриті тести: pytest tests/test_lab_08.py
"""
import os
import signal
import sys


def run_foreground(argv: list[str]) -> int:
    """Запускає програму на передньому плані з правильною обробкою SIGINT."""
    raise NotImplementedError  # TODO: реалізуйте за описом задачі
