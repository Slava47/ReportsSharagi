"""Интерфейс командной строки (CLI) для CodeLab Assistant.

Позволяет генерировать отчеты через командную строку.
"""

import argparse
import os
import sys

from .analyzer import analyze_code
from .executor import run_tests
from .flowchart import generate_flowchart
from .profiles import list_profiles, load_profile, save_profile
from .report_generator import generate_report


def parse_args(args=None):
    """Разбирает аргументы командной строки.

    Args:
        args: Список аргументов (по умолчанию sys.argv).

    Returns:
        Объект с разобранными аргументами.
    """
    parser = argparse.ArgumentParser(
        prog="codelab",
        description="CodeLab Assistant - генератор отчетов для лабораторных работ",
    )

    subparsers = parser.add_subparsers(dest="command", help="Команда")

    # Команда generate
    gen_parser = subparsers.add_parser("generate", help="Сгенерировать отчет")
    gen_parser.add_argument(
        "source_file",
        help="Путь к файлу с исходным кодом (.pas, .py, .cpp)",
    )
    gen_parser.add_argument(
        "--test-data", "-t",
        nargs="*",
        default=[],
        help="Тестовые данные (каждый аргумент — отдельный тест)",
    )
    gen_parser.add_argument(
        "--test-file", "-T",
        help="Файл с тестовыми данными (тесты разделены строкой '---')",
    )
    gen_parser.add_argument(
        "--name", "-n",
        default="Студент",
        help="ФИО студента",
    )
    gen_parser.add_argument(
        "--group", "-g",
        default="",
        help="Номер группы",
    )
    gen_parser.add_argument(
        "--variant", "-v",
        default="",
        help="Номер варианта",
    )
    gen_parser.add_argument(
        "--profile", "-p",
        default="default",
        help="Профиль преподавателя",
    )
    gen_parser.add_argument(
        "--output", "-o",
        default=None,
        help="Путь к выходному файлу (.docx)",
    )

    # Команда profiles
    prof_parser = subparsers.add_parser("profiles", help="Управление профилями")
    prof_parser.add_argument(
        "action",
        choices=["list", "show", "create"],
        help="Действие с профилями",
    )
    prof_parser.add_argument(
        "--name",
        default="default",
        help="Имя профиля",
    )

    return parser.parse_args(args)


def _load_test_data(args):
    """Загружает тестовые данные из аргументов.

    Args:
        args: Разобранные аргументы CLI.

    Returns:
        Список строк с тестовыми данными.
    """
    test_cases = []

    # Из аргументов командной строки
    if args.test_data:
        test_cases.extend(args.test_data)

    # Из файла
    if args.test_file and os.path.exists(args.test_file):
        with open(args.test_file, "r", encoding="utf-8") as f:
            content = f.read()
        # Разделяем тесты по '---'
        parts = content.split("---")
        test_cases.extend(part.strip() for part in parts if part.strip())

    return test_cases


def cmd_generate(args):
    """Обработчик команды generate.

    Args:
        args: Разобранные аргументы CLI.

    Returns:
        Код возврата (0 — успех).
    """
    source_file = args.source_file

    if not os.path.exists(source_file):
        print(f"Ошибка: файл не найден: {source_file}", file=sys.stderr)
        return 1

    # 1. Анализ кода
    print(f"Анализ файла: {source_file}...")
    try:
        analysis = analyze_code(source_file)
    except ValueError as e:
        print(f"Ошибка: {e}", file=sys.stderr)
        return 1

    print(f"  Язык: {analysis['language_display']}")
    print(f"  Цель: {analysis['purpose']}")
    if analysis["algorithms"]:
        print(f"  Алгоритмы: {', '.join(analysis['algorithms'])}")

    # 2. Тестирование
    test_cases = _load_test_data(args)
    test_results = None

    if test_cases:
        print(f"Запуск тестов ({len(test_cases)} шт.)...")
        test_results = run_tests(source_file, analysis["language"], test_cases)

        if test_results["compiled"]:
            for result in test_results["results"]:
                status = "✓" if result["returncode"] == 0 else "✗"
                print(f"  Тест {result['test_number']}: {status}")
        else:
            print(f"  Ошибка компиляции: {test_results['compile_error']}")
    else:
        print("Тестовые данные не указаны, раздел тестирования будет пустым.")

    # 3. Блок-схема
    print("Генерация блок-схемы...")
    flowchart_path = generate_flowchart(analysis["code"], analysis["language"])
    if flowchart_path:
        print(f"  Блок-схема: {flowchart_path}")
    else:
        print("  Блок-схема не сгенерирована (Graphviz не найден)")

    # 4. Генерация отчета
    print("Генерация отчета...")
    student_info = {
        "name": args.name,
        "group": args.group,
        "variant": args.variant,
    }

    output_path = generate_report(
        analysis=analysis,
        test_results=test_results,
        flowchart_path=flowchart_path,
        student_info=student_info,
        profile_name=args.profile,
        output_path=args.output,
    )

    print(f"Отчет сохранен: {output_path}")
    return 0


def cmd_profiles(args):
    """Обработчик команды profiles.

    Args:
        args: Разобранные аргументы CLI.

    Returns:
        Код возврата (0 — успех).
    """
    if args.action == "list":
        profiles = list_profiles()
        print("Доступные профили:")
        for name in profiles:
            profile = load_profile(name)
            display = profile.get("display_name", name)
            print(f"  - {name} ({display})")

    elif args.action == "show":
        profile = load_profile(args.name)
        print(f"Профиль: {args.name}")
        for key, value in profile.items():
            print(f"  {key}: {value}")

    elif args.action == "create":
        profile = load_profile("default")
        profile["name"] = args.name
        profile["display_name"] = args.name
        save_profile(args.name, profile)
        print(f"Профиль '{args.name}' создан.")

    return 0


def main(args=None):
    """Главная функция CLI.

    Args:
        args: Список аргументов (для тестирования).

    Returns:
        Код возврата.
    """
    parsed = parse_args(args)

    if parsed.command == "generate":
        return cmd_generate(parsed)
    elif parsed.command == "profiles":
        return cmd_profiles(parsed)
    else:
        parse_args(["--help"])
        return 0


if __name__ == "__main__":
    sys.exit(main())
