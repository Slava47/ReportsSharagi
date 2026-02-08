"""Модуль генерации блок-схем.

Создает блок-схемы алгоритмов на основе анализа исходного кода
с использованием библиотеки graphviz.
"""

import os
import re
import tempfile

try:
    import graphviz
    GRAPHVIZ_AVAILABLE = True
except ImportError:
    GRAPHVIZ_AVAILABLE = False


def _parse_structure(code, language):
    """Разбирает структуру кода для построения блок-схемы.

    Args:
        code: Исходный код.
        language: Язык программирования.

    Returns:
        Список узлов блок-схемы. Каждый узел — словарь с полями:
        - type: тип узла ('start', 'end', 'process', 'decision', 'io')
        - label: текст узла
    """
    nodes = [{"type": "start", "label": "Начало"}]

    lines = code.strip().split("\n")

    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue

        # Пропускаем комментарии
        if language == "python" and stripped.startswith("#"):
            continue
        if language in ("cpp", "pascal") and stripped.startswith("//"):
            continue

        # Пропускаем декларативные строки
        if language == "pascal" and stripped.lower() in (
            "program", "begin", "end.", "end;", "var", "uses",
        ):
            continue
        if language == "pascal" and stripped.lower().startswith("program "):
            continue
        if language == "pascal" and stripped.lower().startswith("var"):
            continue
        if language == "pascal" and stripped.lower().startswith("uses "):
            continue
        if language == "cpp" and stripped.startswith("#include"):
            continue
        if language == "cpp" and stripped in ("{", "}", "};"):
            continue
        if language == "cpp" and stripped.startswith("using namespace"):
            continue
        if language == "python" and stripped.startswith("import "):
            continue
        if language == "python" and stripped.startswith("from "):
            continue
        if language == "python" and stripped.startswith("def "):
            continue
        if language == "cpp" and re.match(r"int\s+main\s*\(", stripped):
            continue

        # Ввод/вывод
        if _is_io_statement(stripped, language):
            label = _extract_io_label(stripped, language)
            nodes.append({"type": "io", "label": label})
            continue

        # Условия
        if _is_condition(stripped, language):
            label = _extract_condition_label(stripped, language)
            nodes.append({"type": "decision", "label": label})
            continue

        # Циклы
        if _is_loop(stripped, language):
            label = _extract_loop_label(stripped, language)
            nodes.append({"type": "decision", "label": label})
            continue

        # Присваивание и другие операции
        if _is_assignment(stripped, language):
            nodes.append({"type": "process", "label": stripped.rstrip(";")})

    nodes.append({"type": "end", "label": "Конец"})
    return nodes


def _is_io_statement(line, language):
    """Проверяет, является ли строка операцией ввода/вывода."""
    line_lower = line.lower()
    if language == "pascal":
        return any(kw in line_lower for kw in ["readln", "read(", "writeln", "write("])
    elif language == "python":
        return any(kw in line_lower for kw in ["input(", "print("])
    elif language == "cpp":
        return any(kw in line_lower for kw in ["cin", "cout", "scanf", "printf"])
    return False


def _extract_io_label(line, language):
    """Извлекает метку для узла ввода/вывода."""
    line_lower = line.lower()
    if language == "pascal":
        if "readln" in line_lower or "read(" in line_lower:
            return "Ввод данных"
        return "Вывод данных"
    elif language == "python":
        if "input(" in line_lower:
            return "Ввод данных"
        return "Вывод данных"
    elif language == "cpp":
        if "cin" in line_lower or "scanf" in line_lower:
            return "Ввод данных"
        return "Вывод данных"
    return line


def _is_condition(line, language):
    """Проверяет, является ли строка условным оператором."""
    line_lower = line.lower().strip()
    if language == "pascal":
        return line_lower.startswith("if ")
    elif language == "python":
        return line_lower.startswith("if ") or line_lower.startswith("elif ")
    elif language == "cpp":
        return line_lower.startswith("if ") or line_lower.startswith("if(")
    return False


def _extract_condition_label(line, language):
    """Извлекает условие из строки."""
    if language == "pascal":
        match = re.search(r"if\s+(.+?)\s+then", line, re.IGNORECASE)
        if match:
            return match.group(1)
    elif language == "python":
        match = re.search(r"(?:el)?if\s+(.+?):", line)
        if match:
            return match.group(1)
    elif language == "cpp":
        match = re.search(r"if\s*\((.+?)\)", line)
        if match:
            return match.group(1)
    return line.strip()


def _is_loop(line, language):
    """Проверяет, является ли строка циклом."""
    line_lower = line.lower().strip()
    if language == "pascal":
        return any(line_lower.startswith(kw) for kw in ["for ", "while ", "repeat"])
    elif language == "python":
        return any(line_lower.startswith(kw) for kw in ["for ", "while "])
    elif language == "cpp":
        return any(
            line_lower.startswith(kw)
            for kw in ["for ", "for(", "while ", "while(", "do "]
        )
    return False


def _extract_loop_label(line, language):
    """Извлекает условие цикла из строки."""
    if language == "pascal":
        if line.lower().startswith("for"):
            match = re.search(r"for\s+(.+?)\s+do", line, re.IGNORECASE)
            if match:
                return f"Цикл: {match.group(1)}"
        elif line.lower().startswith("while"):
            match = re.search(r"while\s+(.+?)\s+do", line, re.IGNORECASE)
            if match:
                return f"Цикл: {match.group(1)}"
        return f"Цикл: {line.strip()}"
    elif language == "python":
        match = re.search(r"(?:for|while)\s+(.+?):", line)
        if match:
            return f"Цикл: {match.group(1)}"
    elif language == "cpp":
        match = re.search(r"(?:for|while)\s*\((.+?)\)", line)
        if match:
            return f"Цикл: {match.group(1)}"
    return f"Цикл: {line.strip()}"


def _is_assignment(line, language):
    """Проверяет, является ли строка присваиванием."""
    if language == "pascal":
        return ":=" in line
    elif language == "python":
        return "=" in line and not line.strip().startswith(("if ", "while ", "for "))
    elif language == "cpp":
        return "=" in line and not line.strip().startswith(("if ", "while ", "for "))
    return False


# Формы узлов graphviz
NODE_SHAPES = {
    "start": "ellipse",
    "end": "ellipse",
    "process": "box",
    "decision": "diamond",
    "io": "parallelogram",
}


def generate_flowchart(code, language, output_path=None):
    """Генерирует блок-схему алгоритма.

    Args:
        code: Исходный код.
        language: Язык программирования.
        output_path: Путь для сохранения изображения (без расширения).
            Если None, используется временный файл.

    Returns:
        Путь к сгенерированному файлу изображения (PNG) или None при ошибке.
    """
    if not GRAPHVIZ_AVAILABLE:
        return None

    nodes = _parse_structure(code, language)

    if len(nodes) <= 2:
        # Только начало и конец - нечего рисовать
        return None

    dot = graphviz.Digraph(format="png")
    dot.attr(rankdir="TB", fontname="Arial", fontsize="12")
    dot.attr("node", fontname="Arial", fontsize="10")

    # Добавляем узлы
    for i, node in enumerate(nodes):
        node_id = f"n{i}"
        shape = NODE_SHAPES.get(node["type"], "box")

        if node["type"] == "io":
            # Параллелограмм эмулируется через shape и style
            dot.node(node_id, node["label"], shape="parallelogram",
                     style="filled", fillcolor="#E8F5E9")
        elif node["type"] == "decision":
            dot.node(node_id, node["label"], shape="diamond",
                     style="filled", fillcolor="#FFF9C4")
        elif node["type"] in ("start", "end"):
            dot.node(node_id, node["label"], shape="ellipse",
                     style="filled", fillcolor="#BBDEFB")
        else:
            dot.node(node_id, node["label"], shape="box",
                     style="filled", fillcolor="#F5F5F5")

    # Добавляем связи
    for i in range(len(nodes) - 1):
        dot.edge(f"n{i}", f"n{i+1}")

    # Сохраняем
    if output_path is None:
        tmpdir = tempfile.mkdtemp()
        output_path = os.path.join(tmpdir, "flowchart")

    try:
        rendered = dot.render(output_path, cleanup=True)
        return rendered
    except graphviz.backend.execute.ExecutableNotFound:
        return None
    except Exception:
        return None
