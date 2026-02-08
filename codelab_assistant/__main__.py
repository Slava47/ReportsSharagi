"""Главная точка входа для CodeLab Assistant.

Запуск через: python -m codelab_assistant [аргументы]
Без аргументов открывается GUI.
С аргументами работает CLI.
"""

import sys

from .cli import main as cli_main


def main():
    """Точка входа: CLI с аргументами, GUI без аргументов."""
    if len(sys.argv) > 1:
        sys.exit(cli_main())
    else:
        try:
            from .gui import main as gui_main
            gui_main()
        except ImportError:
            print(
                "Графический интерфейс недоступен (tkinter не установлен).\n"
                "Используйте CLI: python -m codelab_assistant generate <файл>"
            )
            sys.exit(1)


if __name__ == "__main__":
    main()
