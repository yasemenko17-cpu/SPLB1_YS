import os
import sys
import signal

def run_foreground(argv: list[str]) -> int:
    """
    Запускає зовнішню команду на передньому плані з правильним керуванням SIGINT.
    """
    if not argv:
        return 0

    # 1. Перед fork батько ігнорує SIGINT і запам'ятовує попередній обробник
    orig_handler = signal.signal(signal.SIGINT, signal.SIG_IGN)
    
    # Скидаємо буфери перед fork
    sys.stdout.flush()
    sys.stderr.flush()

    try:
        pid = os.fork()
        if pid == 0:
            # 2. У дитині повертаємо стандартну поведінку SIG_DFL перед exec
            signal.signal(signal.SIGINT, signal.SIG_DFL)
            try:
                os.execvpe(argv[0], argv, os.environ)
            except FileNotFoundError:
                sys.stderr.write(f"pysh: {argv[0]}: команду не знайдено\n")
                os._exit(127)
            except PermissionError:
                sys.stderr.write(f"pysh: {argv[0]}: немає дозволу на виконання\n")
                os._exit(126)
            except OSError:
                os._exit(127)
        else:
            # 3. Батько чекає на дитину, захищаючись від переривань signal
            while True:
                try:
                    _, status = os.waitpid(pid, 0)
                    break
                except InterruptedError:
                    continue

            # Розшифрування статусу завершення процесу
            if os.WIFEXITED(status):
                return os.WEXITSTATUS(status)
            elif os.WIFSIGNALED(status):
                sig = os.WTERMSIG(status)
                return 128 + sig
            return 0
    finally:
        # 4. Відновлюємо попередній обробник SIGINT у блоці finally за будь-яких обставин
        signal.signal(signal.SIGINT, orig_handler)