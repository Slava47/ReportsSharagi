"""Тесты для модуля профилей преподавателей."""

import json
import os
import tempfile

import pytest

from codelab_assistant.profiles import (
    DEFAULT_PROFILE,
    delete_profile,
    list_profiles,
    load_profile,
    save_profile,
)


class TestDefaultProfile:
    """Тесты профиля по умолчанию."""

    def test_has_required_fields(self):
        assert "font_name" in DEFAULT_PROFILE
        assert "font_size" in DEFAULT_PROFILE
        assert "sections" in DEFAULT_PROFILE

    def test_default_font(self):
        assert DEFAULT_PROFILE["font_name"] == "Times New Roman"

    def test_default_font_size(self):
        assert DEFAULT_PROFILE["font_size"] == 14

    def test_sections_include_required(self):
        sections = DEFAULT_PROFILE["sections"]
        assert "title_page" in sections
        assert "listing" in sections
        assert "conclusion" in sections


class TestLoadProfile:
    """Тесты загрузки профилей."""

    def test_load_default(self):
        profile = load_profile("default")
        assert profile["name"] == "default"
        assert profile["font_name"] == "Times New Roman"

    def test_load_nonexistent_returns_default(self):
        profile = load_profile("nonexistent_profile_xyz")
        assert profile["font_name"] == DEFAULT_PROFILE["font_name"]


class TestSaveAndDeleteProfile:
    """Тесты сохранения и удаления профилей."""

    def test_save_and_load(self):
        test_profile = DEFAULT_PROFILE.copy()
        test_profile["name"] = "test_teacher"
        test_profile["font_name"] = "Arial"
        test_profile["font_size"] = 12

        try:
            save_profile("test_teacher", test_profile)
            loaded = load_profile("test_teacher")
            assert loaded["font_name"] == "Arial"
            assert loaded["font_size"] == 12
        finally:
            delete_profile("test_teacher")

    def test_delete_default_fails(self):
        assert delete_profile("default") is False

    def test_delete_nonexistent(self):
        assert delete_profile("nonexistent_xyz") is False


class TestListProfiles:
    """Тесты списка профилей."""

    def test_includes_default(self):
        profiles = list_profiles()
        assert "default" in profiles
