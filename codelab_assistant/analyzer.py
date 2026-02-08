"""Модуль анализа исходного кода.

Определяет язык программирования, извлекает комментарии,
анализирует структуру и алгоритмы в коде.
"""

import os
import re


# Поддерживаемые языки и их расширения
LANGUAGE_EXTENSIONS = {
    ".pas": "pascal",
    ".py": "python",
    ".cpp": "cpp",
    ".cc": "cpp",
    ".cxx": "cpp",
    ".c": "cpp",
}

# Паттерны комментариев для каждого языка
COMMENT_PATTERNS = {
    "pascal": {
        "single": r"\{([^}]*)\}",
        "single_alt": r"\(\*([^*]*)\*\)",
        "line": r"//(.*)$",
    },
    "python": {
        "line": r"#(.*)$",
        "multi_start": r'"""',
        "multi_end": r'"""',
    },
    "cpp": {
        "line": r"//(.*)$",
        "multi_start": r"/\*",
        "multi_end": r"\*/",
    },
}

# Ключевые слова для определения алгоритмов
ALGORITHM_KEYWORDS = {
    "сортировка": ["sort", "bubble", "quick", "merge", "insertion", "selection"],
    "поиск": ["search", "find", "binary", "linear"],
    "рекурсия": ["recursive", "recursion", "factorial", "fibonacci"],
    "цикл": ["for", "while", "repeat", "loop"],
    "массив": ["array", "list", "vector", "arr"],
    "строки": ["string", "str", "char", "text"],
    "файлы": ["file", "open", "read", "write", "close"],
    "математика": ["math", "sqrt", "pow", "abs", "sin", "cos"],
}


def detect_language(filepath):
    """Определяет язык программирования по расширению файла.

    Args:
        filepath: Путь к файлу с исходным кодом.

    Returns:
        Название языка ('pascal', 'python', 'cpp') или None.
    """
    ext = os.path.splitext(filepath)[1].lower()
    return LANGUAGE_EXTENSIONS.get(ext)


def extract_comments(code, language):
    """Извлекает комментарии из исходного кода.

    Args:
        code: Строка с исходным кодом.
        language: Язык программирования.

    Returns:
        Список строк-комментариев.
    """
    comments = []

    if language == "pascal":
        # Комментарии в фигурных скобках
        for match in re.finditer(r"\{([^}]*)\}", code):
            comments.append(match.group(1).strip())
        # Комментарии (* ... *)
        for match in re.finditer(r"\(\*(.*?)\*\)", code, re.DOTALL):
            comments.append(match.group(1).strip())
        # Однострочные комментарии //
        for match in re.finditer(r"//(.*)$", code, re.MULTILINE):
            comments.append(match.group(1).strip())

    elif language == "python":
        # Однострочные комментарии #
        for match in re.finditer(r"#(.*)$", code, re.MULTILINE):
            comments.append(match.group(1).strip())
        # Многострочные строки-комментарии """..."""
        for match in re.finditer(r'"""(.*?)"""', code, re.DOTALL):
            comments.append(match.group(1).strip())
        # Многострочные строки-комментарии '''...'''
        for match in re.finditer(r"'''(.*?)'''", code, re.DOTALL):
            comments.append(match.group(1).strip())

    elif language == "cpp":
        # Однострочные комментарии //
        for match in re.finditer(r"//(.*)$", code, re.MULTILINE):
            comments.append(match.group(1).strip())
        # Многострочные комментарии /* ... */
        for match in re.finditer(r"/\*(.*?)\*/", code, re.DOTALL):
            comments.append(match.group(1).strip())

    return [c for c in comments if c]


def detect_algorithms(code):
    """Определяет используемые алгоритмы по ключевым словам.

    Args:
        code: Строка с исходным кодом.

    Returns:
        Список названий обнаруженных алгоритмических концепций.
    """
    code_lower = code.lower()
    detected = []

    for algorithm_name, keywords in ALGORITHM_KEYWORDS.items():
        for keyword in keywords:
            if keyword in code_lower:
                detected.append(algorithm_name)
                break

    return detected


def extract_purpose(code, language, filepath):
    """Определяет цель программы из комментариев или имени файла.

    Args:
        code: Строка с исходным кодом.
        language: Язык программирования.
        filepath: Путь к файлу.

    Returns:
        Строка с описанием цели работы.
    """
    comments = extract_comments(code, language)

    # Ищем комментарий, похожий на описание цели
    purpose_keywords = [
        "цель", "задание", "задача", "лабораторная",
        "purpose", "task", "lab", "objective",
    ]

    for comment in comments:
        comment_lower = comment.lower()
        for keyword in purpose_keywords:
            if keyword in comment_lower:
                return comment

    # Если в комментариях не нашли — берём первый комментарий
    if comments:
        return comments[0]

    # Иначе формируем из имени файла
    basename = os.path.splitext(os.path.basename(filepath))[0]
    return f"Выполнение программы '{basename}'"


def get_language_display_name(language):
    """Возвращает отображаемое название языка.

    Args:
        language: Внутреннее название языка.

    Returns:
        Строка с отображаемым названием.
    """
    names = {
        "pascal": "Pascal",
        "python": "Python",
        "cpp": "C++",
    }
    return names.get(language, language)


def analyze_code(filepath):
    """Полный анализ исходного кода.

    Args:
        filepath: Путь к файлу с исходным кодом.

    Returns:
        Словарь с результатами анализа:
        - language: язык программирования
        - language_display: отображаемое название языка
        - comments: список комментариев
        - algorithms: список алгоритмов
        - purpose: цель работы
        - code: исходный код
        - filename: имя файла
    """
    language = detect_language(filepath)
    if language is None:
        raise ValueError(
            f"Неподдерживаемый формат файла: {filepath}. "
            f"Поддерживаются: {', '.join(LANGUAGE_EXTENSIONS.keys())}"
        )

    with open(filepath, "r", encoding="utf-8") as f:
        code = f.read()

    return {
        "language": language,
        "language_display": get_language_display_name(language),
        "comments": extract_comments(code, language),
        "algorithms": detect_algorithms(code),
        "purpose": extract_purpose(code, language, filepath),
        "code": code,
        "filename": os.path.basename(filepath),
    }
