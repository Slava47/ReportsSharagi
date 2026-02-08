"""Тесты для модуля генерации отчетов."""

import os
import tempfile

import pytest

from codelab_assistant.report_generator import generate_report


class TestGenerateReport:
    """Тесты генерации отчетов."""

    def _make_analysis(self):
        """Создает тестовые данные анализа."""
        return {
            "language": "python",
            "language_display": "Python",
            "comments": ["Тестовая программа"],
            "algorithms": ["цикл"],
            "purpose": "Тестирование генерации отчета",
            "code": "# Тестовая программа\nfor i in range(10):\n    print(i)\n",
            "filename": "test_program.py",
        }

    def test_generate_report_creates_file(self):
        analysis = self._make_analysis()
        with tempfile.TemporaryDirectory() as tmpdir:
            output = os.path.join(tmpdir, "test_report.docx")
            result = generate_report(
                analysis=analysis,
                output_path=output,
            )
            assert os.path.exists(result)
            assert result.endswith(".docx")

    def test_generate_with_student_info(self):
        analysis = self._make_analysis()
        student = {
            "name": "Иванов Иван Иванович",
            "group": "ИТ-21",
            "variant": "5",
        }
        with tempfile.TemporaryDirectory() as tmpdir:
            output = os.path.join(tmpdir, "test_report.docx")
            result = generate_report(
                analysis=analysis,
                student_info=student,
                output_path=output,
            )
            assert os.path.exists(result)

    def test_generate_with_test_results(self):
        analysis = self._make_analysis()
        test_results = {
            "compiled": True,
            "compile_error": None,
            "results": [
                {
                    "test_number": 1,
                    "input": "5",
                    "stdout": "0\n1\n2\n3\n4\n",
                    "stderr": "",
                    "returncode": 0,
                    "error": None,
                },
            ],
        }
        with tempfile.TemporaryDirectory() as tmpdir:
            output = os.path.join(tmpdir, "test_report.docx")
            result = generate_report(
                analysis=analysis,
                test_results=test_results,
                output_path=output,
            )
            assert os.path.exists(result)

    def test_generate_with_compile_error(self):
        analysis = self._make_analysis()
        test_results = {
            "compiled": False,
            "compile_error": "Syntax error",
            "results": [],
        }
        with tempfile.TemporaryDirectory() as tmpdir:
            output = os.path.join(tmpdir, "test_report.docx")
            result = generate_report(
                analysis=analysis,
                test_results=test_results,
                output_path=output,
            )
            assert os.path.exists(result)

    def test_generate_without_test_results(self):
        analysis = self._make_analysis()
        with tempfile.TemporaryDirectory() as tmpdir:
            output = os.path.join(tmpdir, "test_report.docx")
            result = generate_report(
                analysis=analysis,
                test_results=None,
                output_path=output,
            )
            assert os.path.exists(result)

    def test_default_output_path(self):
        analysis = self._make_analysis()
        result = generate_report(analysis=analysis)
        assert os.path.exists(result)
        assert "report_test_program.docx" in result
        # Cleanup
        os.unlink(result)

    def test_generate_with_title_overrides(self):
        analysis = self._make_analysis()
        overrides = {
            "university": "МГУ им. Ломоносова",
            "faculty": "Факультет ВМК",
            "department": "Кафедра информатики",
        }
        with tempfile.TemporaryDirectory() as tmpdir:
            output = os.path.join(tmpdir, "test_report.docx")
            result = generate_report(
                analysis=analysis,
                output_path=output,
                title_overrides=overrides,
            )
            assert os.path.exists(result)

    def test_generate_with_extra_tasks(self):
        analysis = self._make_analysis()
        extra_analysis = self._make_analysis()
        extra_analysis["filename"] = "task2.py"
        extra_analysis["task_label"] = "Задание 2"
        with tempfile.TemporaryDirectory() as tmpdir:
            output = os.path.join(tmpdir, "test_report.docx")
            result = generate_report(
                analysis=analysis,
                output_path=output,
                extra_tasks=[
                    {"analysis": extra_analysis, "flowchart_path": None},
                ],
            )
            assert os.path.exists(result)

    def test_generate_with_task_label(self):
        analysis = self._make_analysis()
        analysis["task_label"] = "Задание 1"
        with tempfile.TemporaryDirectory() as tmpdir:
            output = os.path.join(tmpdir, "test_report.docx")
            result = generate_report(
                analysis=analysis,
                output_path=output,
            )
            assert os.path.exists(result)
