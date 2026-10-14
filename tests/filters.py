"""Допоміжні маленькі «команди» для тестів: працюють однаково на будь-якому Linux.

Запуск:  python tests/filters.py <команда> [аргументи]
Приклад: python tests/filters.py words груша яблуко | python tests/filters.py sort
"""
import os
import signal
import sys
import time


def main(argv):
    cmd, args = argv[1], argv[2:]
    if cmd == "words":                      # кожне слово — в окремому рядку
        for word in args:
            print(word)
    elif cmd == "gen":                      # числа 0..N-1
        for i in range(int(args[0])):
            print(i)
    elif cmd == "cat":                      # копіює вхід на вихід
        sys.stdout.write(sys.stdin.read())
    elif cmd == "upper":
        sys.stdout.write(sys.stdin.read().upper())
    elif cmd == "lower":
        sys.stdout.write(sys.stdin.read().lower())
    elif cmd == "sort":
        sys.stdout.write("".join(sorted(sys.stdin.readlines())))
    elif cmd == "rev":                      # рядки у зворотному порядку
        sys.stdout.write("".join(reversed(sys.stdin.readlines())))
    elif cmd == "count":                    # кількість рядків входу
        print(sum(1 for _ in sys.stdin))
    elif cmd == "head":                     # перші N рядків (вхід читається повністю)
        sys.stdout.write("".join(sys.stdin.readlines()[: int(args[0])]))
    elif cmd == "exit":                     # завершується з кодом N
        sys.exit(int(args[0]))
    elif cmd == "kill":                     # вбиває сам себе сигналом (SIGKILL, SIGTERM, SIGINT ...)
        number = getattr(signal, args[0])
        if number not in (signal.SIGKILL, signal.SIGSTOP):
            signal.signal(number, signal.SIG_DFL)
        os.kill(os.getpid(), number)
        time.sleep(5)
    elif cmd == "env":                      # друкує значення змінної оточення
        print(os.environ.get(args[0], "<немає>"))
    elif cmd == "cwd":                      # друкує поточний каталог
        print(os.getcwd())
    elif cmd == "fd-check":                 # скільки відкритих дескрипторів, окрім 0,1,2
        print(len([n for n in os.listdir("/proc/self/fd") if int(n) > 2]) - 1)
    elif cmd == "inherit-check":            # код 5, якщо SIGINT успадковано як «ігнорувати»
        sys.exit(5 if signal.getsignal(signal.SIGINT) is signal.SIG_IGN else 0)
    elif cmd == "signal-parent":            # [пауза] і сигнал батьківському процесу; завершується з 0
        if len(args) > 1:
            time.sleep(float(args[1]))
        os.kill(os.getppid(), getattr(signal, args[0]))
    elif cmd == "exit-env":                 # завершується з кодом, записаним у змінній оточення
        sys.exit(int(os.environ[args[0]]))
    elif cmd == "fail":                     # читає весь вхід, нічого не друкує, завершується з кодом N
        sys.stdin.read()
        sys.exit(int(args[0]))
    elif cmd == "sleep":
        time.sleep(float(args[0]))
    else:
        sys.exit("невідома команда: " + cmd)


if __name__ == "__main__":
    main(sys.argv)
