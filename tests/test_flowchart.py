"""Тесты для модуля генерации блок-схем."""

import pytest

from codelab_assistant.flowchart import (
    _extract_condition_label,
    _extract_io_label,
    _extract_loop_label,
    _is_assignment,
    _is_condition,
    _is_io_statement,
    _is_loop,
    _parse_structure,
)


class TestIsIOStatement:
    """Тесты определения операций ввода/вывода."""

    def test_python_print(self):
        assert _is_io_statement("print('hello')", "python")

    def test_python_input(self):
        assert _is_io_statement("x = input()", "python")

    def test_cpp_cout(self):
        assert _is_io_statement("cout << x;", "cpp")

    def test_cpp_cin(self):
        assert _is_io_statement("cin >> x;", "cpp")

    def test_pascal_writeln(self):
        assert _is_io_statement("writeln('hello');", "pascal")

    def test_pascal_readln(self):
        assert _is_io_statement("readln(x);", "pascal")

    def test_not_io(self):
        assert not _is_io_statement("x = 1", "python")


class TestIsCondition:
    """Тесты определения условных операторов."""

    def test_python_if(self):
        assert _is_condition("if x > 0:", "python")

    def test_python_elif(self):
        assert _is_condition("elif x < 0:", "python")

    def test_cpp_if(self):
        assert _is_condition("if (x > 0) {", "cpp")

    def test_pascal_if(self):
        assert _is_condition("if x > 0 then", "pascal")

    def test_not_condition(self):
        assert not _is_condition("x = 1", "python")


class TestIsLoop:
    """Тесты определения циклов."""

    def test_python_for(self):
        assert _is_loop("for i in range(10):", "python")

    def test_python_while(self):
        assert _is_loop("while x > 0:", "python")

    def test_cpp_for(self):
        assert _is_loop("for (int i = 0; i < 10; i++) {", "cpp")

    def test_pascal_for(self):
        assert _is_loop("for i := 1 to 10 do", "pascal")

    def test_not_loop(self):
        assert not _is_loop("x = 1", "python")


class TestParseStructure:
    """Тесты разбора структуры кода."""

    def test_simple_python(self):
        code = "x = int(input())\nprint(x * 2)"
        nodes = _parse_structure(code, "python")
        assert nodes[0]["type"] == "start"
        assert nodes[-1]["type"] == "end"
        assert len(nodes) >= 3

    def test_with_condition(self):
        code = "x = 1\nif x > 0:\n    print(x)"
        nodes = _parse_structure(code, "python")
        types = [n["type"] for n in nodes]
        assert "decision" in types

    def test_start_and_end_always_present(self):
        code = ""
        nodes = _parse_structure(code, "python")
        assert nodes[0]["type"] == "start"
        assert nodes[-1]["type"] == "end"


class TestExtractLabels:
    """Тесты извлечения меток."""

    def test_io_input_python(self):
        label = _extract_io_label("x = input()", "python")
        assert "ввод" in label.lower()

    def test_io_output_python(self):
        label = _extract_io_label("print(x)", "python")
        assert "вывод" in label.lower()

    def test_condition_python(self):
        label = _extract_condition_label("if x > 0:", "python")
        assert "x > 0" in label

    def test_loop_python(self):
        label = _extract_loop_label("for i in range(10):", "python")
        assert "i in range(10)" in label
