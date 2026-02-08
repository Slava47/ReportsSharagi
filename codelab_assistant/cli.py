"""Интерфейс командной строки (CLI) для CodeLab Assistant.

Позволяет генерировать отчеты через командную строку.
"""

import argparse
import os
import sys

from .analyzer import analyze_code
from .executor import run_tests
from .flowchart import generate_flowchart, generate_mermaid_code, save_mermaid_code
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
        "--extra-files", "-e",
        nargs="*",
        default=[],
        help="Дополнительные файлы заданий (каждый — отдельное задание)",
    )
    gen_parser.add_argument(
        "--labels", "-l",
        nargs="*",
        default=[],
        help="Подписи к файлам заданий (в порядке: основной, доп. файлы)",
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
        "--university",
        default="",
        help="Название университета",
    )
    gen_parser.add_argument(
        "--faculty",
        default="",
        help="Название факультета",
    )
    gen_parser.add_argument(
        "--department",
        default="",
        help="Название кафедры",
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


def _save_mermaid_alongside(output_path, mermaid_code, suffix=""):
    """Сохраняет Mermaid-код рядом с файлом отчета.

    Args:
        output_path: Путь к .docx файлу.
        mermaid_code: Строка с Mermaid-кодом.
        suffix: Дополнительный суффикс к имени файла.

    Returns:
        Путь к сохранённому файлу или None.
    """
    if not mermaid_code or not output_path:
        return None
    base = os.path.splitext(output_path)[0]
    mermaid_path = f"{base}{suffix}_flowchart.mmd"
    return save_mermaid_code(mermaid_code, mermaid_path)


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

    # Собираем все файлы заданий
    all_files = [source_file]
    if args.extra_files:
        for ef in args.extra_files:
            if not os.path.exists(ef):
                print(f"Ошибка: файл не найден: {ef}", file=sys.stderr)
                return 1
            all_files.append(ef)

    # Подписи к файлам
    labels = list(args.labels) if args.labels else []

    # Анализируем все файлы
    analyses = []
    for i, fpath in enumerate(all_files):
        print(f"Анализ файла: {fpath}...")
        try:
            analysis = analyze_code(fpath)
        except ValueError as e:
            print(f"Ошибка: {e}", file=sys.stderr)
            return 1

        if i < len(labels):
            analysis["task_label"] = labels[i]
        else:
            analysis["task_label"] = ""

        print(f"  Язык: {analysis['language_display']}")
        print(f"  Цель: {analysis['purpose']}")
        if analysis["algorithms"]:
            print(f"  Алгоритмы: {', '.join(analysis['algorithms'])}")

        analyses.append(analysis)

    # Основной анализ (первый файл)
    analysis = analyses[0]

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

    # 3. Блок-схемы для всех файлов
    flowchart_paths = []
    mermaid_codes = []
    for a in analyses:
        print(f"Генерация блок-схемы для {a['filename']}...")
        fc_path = generate_flowchart(a["code"], a["language"])
        mermaid = generate_mermaid_code(a["code"], a["language"])
        flowchart_paths.append(fc_path)
        mermaid_codes.append(mermaid)
        if fc_path:
            print(f"  Блок-схема: {fc_path}")
        else:
            print("  Блок-схема не сгенерирована (Graphviz не найден)")
        if mermaid:
            print("  Mermaid-код сгенерирован")

    # 4. Генерация отчета
    print("Генерация отчета...")
    student_info = {
        "name": args.name,
        "group": args.group,
        "variant": args.variant,
    }

    # Переопределяем university/faculty/department из CLI-аргументов
    title_overrides = {}
    if args.university:
        title_overrides["university"] = args.university
    if args.faculty:
        title_overrides["faculty"] = args.faculty
    if args.department:
        title_overrides["department"] = args.department

    # Подготовка дополнительных заданий
    extra_tasks = []
    for i in range(1, len(analyses)):
        extra_tasks.append({
            "analysis": analyses[i],
            "flowchart_path": flowchart_paths[i] if i < len(flowchart_paths) else None,
        })

    output_path = generate_report(
        analysis=analysis,
        test_results=test_results,
        flowchart_path=flowchart_paths[0] if flowchart_paths else None,
        student_info=student_info,
        profile_name=args.profile,
        output_path=args.output,
        title_overrides=title_overrides,
        extra_tasks=extra_tasks,
    )

    # 5. Сохраняем Mermaid-код рядом с отчетом
    for i, mermaid in enumerate(mermaid_codes):
        suffix = "" if i == 0 else f"_task{i+1}"
        mmd_path = _save_mermaid_alongside(output_path, mermaid, suffix)
        if mmd_path:
            print(f"  Mermaid-код сохранён: {mmd_path}")

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
