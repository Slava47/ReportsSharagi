"""Тесты для модуля анализатора кода."""

import os
import tempfile

import pytest

from codelab_assistant.analyzer import (
    analyze_code,
    detect_algorithms,
    detect_language,
    extract_comments,
    extract_purpose,
    get_language_display_name,
)


class TestDetectLanguage:
    """Тесты определения языка программирования."""

    def test_pascal(self):
        assert detect_language("lab1.pas") == "pascal"

    def test_python(self):
        assert detect_language("program.py") == "python"

    def test_cpp(self):
        assert detect_language("main.cpp") == "cpp"

    def test_cc(self):
        assert detect_language("main.cc") == "cpp"

    def test_c(self):
        assert detect_language("main.c") == "cpp"

    def test_unsupported(self):
        assert detect_language("script.js") is None

    def test_no_extension(self):
        assert detect_language("Makefile") is None

    def test_case_insensitive(self):
        assert detect_language("Lab1.PAS") == "pascal"

    def test_path_with_directory(self):
        assert detect_language("/home/user/projects/lab1.py") == "python"


class TestExtractComments:
    """Тесты извлечения комментариев."""

    def test_python_single_line(self):
        code = "# This is a comment\nx = 1\n# Another comment"
        comments = extract_comments(code, "python")
        assert "This is a comment" in comments
        assert "Another comment" in comments

    def test_python_multiline(self):
        code = '"""This is a docstring"""\nx = 1'
        comments = extract_comments(code, "python")
        assert "This is a docstring" in comments

    def test_cpp_single_line(self):
        code = "// This is a comment\nint x = 1;"
        comments = extract_comments(code, "cpp")
        assert "This is a comment" in comments

    def test_cpp_multiline(self):
        code = "/* Multi\nline\ncomment */\nint x = 1;"
        comments = extract_comments(code, "cpp")
        assert any("Multi" in c for c in comments)

    def test_pascal_braces(self):
        code = "{ Это комментарий }\nvar x: integer;"
        comments = extract_comments(code, "pascal")
        assert "Это комментарий" in comments

    def test_pascal_parentheses(self):
        code = "(* Это комментарий *)\nvar x: integer;"
        comments = extract_comments(code, "pascal")
        assert "Это комментарий" in comments

    def test_no_comments(self):
        code = "x = 1\ny = 2"
        comments = extract_comments(code, "python")
        assert comments == []


class TestDetectAlgorithms:
    """Тесты определения алгоритмов."""

    def test_sort(self):
        code = "bubble_sort(arr)"
        algos = detect_algorithms(code)
        assert "сортировка" in algos

    def test_search(self):
        code = "result = binary_search(arr, target)"
        algos = detect_algorithms(code)
        assert "поиск" in algos

    def test_loop(self):
        code = "for i in range(10):\n    print(i)"
        algos = detect_algorithms(code)
        assert "цикл" in algos

    def test_no_algorithms(self):
        code = "x = 1"
        algos = detect_algorithms(code)
        assert algos == []


class TestExtractPurpose:
    """Тесты определения цели работы."""

    def test_from_comment(self):
        code = "# Цель: сортировка массива\nx = [3,1,2]"
        purpose = extract_purpose(code, "python", "lab1.py")
        assert "сортировка" in purpose.lower()

    def test_from_filename(self):
        code = "x = 1"
        purpose = extract_purpose(code, "python", "lab1.py")
        assert "lab1" in purpose

    def test_first_comment_fallback(self):
        code = "# Some description\nx = 1"
        purpose = extract_purpose(code, "python", "lab1.py")
        assert "Some description" in purpose


class TestGetLanguageDisplayName:
    """Тесты отображаемых имён языков."""

    def test_pascal(self):
        assert get_language_display_name("pascal") == "Pascal"

    def test_python(self):
        assert get_language_display_name("python") == "Python"

    def test_cpp(self):
        assert get_language_display_name("cpp") == "C++"

    def test_unknown(self):
        assert get_language_display_name("unknown") == "unknown"


class TestAnalyzeCode:
    """Тесты полного анализа кода."""

    def test_analyze_python_file(self):
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".py", delete=False, encoding="utf-8"
        ) as f:
            f.write("# Лабораторная работа: сортировка\n")
            f.write("arr = [3, 1, 2]\n")
            f.write("arr.sort()\n")
            f.write("print(arr)\n")
            tmppath = f.name

        try:
            result = analyze_code(tmppath)
            assert result["language"] == "python"
            assert result["language_display"] == "Python"
            assert len(result["comments"]) > 0
            assert result["code"] is not None
            assert result["filename"].endswith(".py")
        finally:
            os.unlink(tmppath)

    def test_analyze_unsupported_raises(self):
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".js", delete=False
        ) as f:
            f.write("console.log('hello');")
            tmppath = f.name

        try:
            with pytest.raises(ValueError):
                analyze_code(tmppath)
        finally:
            os.unlink(tmppath)
