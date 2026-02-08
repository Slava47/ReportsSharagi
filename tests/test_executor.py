"""Тесты для модуля выполнения кода."""

import os
import tempfile

import pytest

from codelab_assistant.executor import compile_code, run_program, run_tests


class TestCompileCode:
    """Тесты компиляции кода."""

    def test_python_no_compilation(self):
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".py", delete=False
        ) as f:
            f.write("print('hello')")
            tmppath = f.name

        try:
            executable, error = compile_code(tmppath, "python")
            assert executable == tmppath
            assert error is None
        finally:
            os.unlink(tmppath)


class TestRunProgram:
    """Тесты запуска программ."""

    def test_run_python_simple(self):
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".py", delete=False, encoding="utf-8"
        ) as f:
            f.write("print('hello world')")
            tmppath = f.name

        try:
            result = run_program(tmppath, "python")
            assert result["error"] is None
            assert "hello world" in result["stdout"]
            assert result["returncode"] == 0
        finally:
            os.unlink(tmppath)

    def test_run_python_with_input(self):
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".py", delete=False, encoding="utf-8"
        ) as f:
            f.write("x = input()\nprint(f'Got: {x}')")
            tmppath = f.name

        try:
            result = run_program(tmppath, "python", input_data="test_input\n")
            assert result["error"] is None
            assert "Got: test_input" in result["stdout"]
        finally:
            os.unlink(tmppath)

    def test_run_nonexistent_file(self):
        result = run_program("/nonexistent/file.py", "python")
        # Python interpreter runs but reports error via stderr/returncode
        assert result["returncode"] != 0 or result["error"] is not None


class TestRunTests:
    """Тесты запуска тестовых наборов."""

    def test_run_python_tests(self):
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".py", delete=False, encoding="utf-8"
        ) as f:
            f.write("x = int(input())\nprint(x * 2)")
            tmppath = f.name

        try:
            results = run_tests(tmppath, "python", ["5\n", "10\n"])
            assert results["compiled"] is True
            assert len(results["results"]) == 2
            assert "10" in results["results"][0]["stdout"]
            assert "20" in results["results"][1]["stdout"]
        finally:
            os.unlink(tmppath)
