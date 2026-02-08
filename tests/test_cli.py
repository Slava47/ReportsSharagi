"""Тесты для CLI интерфейса."""

import os
import tempfile

import pytest

from codelab_assistant.cli import cmd_profiles, parse_args


class TestParseArgs:
    """Тесты разбора аргументов CLI."""

    def test_generate_command(self):
        args = parse_args(["generate", "test.py"])
        assert args.command == "generate"
        assert args.source_file == "test.py"

    def test_generate_with_options(self):
        args = parse_args([
            "generate", "test.py",
            "--name", "Иванов",
            "--group", "ИТ-21",
            "--variant", "5",
        ])
        assert args.name == "Иванов"
        assert args.group == "ИТ-21"
        assert args.variant == "5"

    def test_generate_with_test_data(self):
        args = parse_args([
            "generate", "test.py",
            "--test-data", "1 2 3", "4 5 6",
        ])
        assert args.test_data == ["1 2 3", "4 5 6"]

    def test_profiles_list(self):
        args = parse_args(["profiles", "list"])
        assert args.command == "profiles"
        assert args.action == "list"

    def test_default_profile(self):
        args = parse_args(["generate", "test.py"])
        assert args.profile == "default"

    def test_generate_with_university(self):
        args = parse_args([
            "generate", "test.py",
            "--university", "МГУ",
            "--faculty", "ВМК",
            "--department", "Информатики",
        ])
        assert args.university == "МГУ"
        assert args.faculty == "ВМК"
        assert args.department == "Информатики"

    def test_default_university_empty(self):
        args = parse_args(["generate", "test.py"])
        assert args.university == ""
        assert args.faculty == ""
        assert args.department == ""

    def test_generate_with_extra_files(self):
        args = parse_args([
            "generate", "test.py",
            "--extra-files", "task2.py", "task3.py",
        ])
        assert args.extra_files == ["task2.py", "task3.py"]

    def test_generate_with_labels(self):
        args = parse_args([
            "generate", "test.py",
            "--labels", "Задание 1", "Задание 2",
        ])
        assert args.labels == ["Задание 1", "Задание 2"]


class TestCmdProfiles:
    """Тесты команды profiles."""

    def test_list_profiles(self, capsys):
        args = parse_args(["profiles", "list"])
        result = cmd_profiles(args)
        assert result == 0
        captured = capsys.readouterr()
        assert "default" in captured.out
