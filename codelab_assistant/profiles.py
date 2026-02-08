"""Модуль управления профилями преподавателей.

Хранит и загружает настройки форматирования отчетов
для конкретных преподавателей.
"""

import json
import os


# Директория для хранения профилей
PROFILES_DIR = os.path.join(os.path.dirname(__file__), "..", "templates")

# Профиль по умолчанию
DEFAULT_PROFILE = {
    "name": "default",
    "display_name": "Стандартный",
    "font_name": "Times New Roman",
    "font_size": 14,
    "code_font_name": "Courier New",
    "code_font_size": 10,
    "margins": {
        "top_cm": 2.0,
        "bottom_cm": 2.0,
        "left_cm": 3.0,
        "right_cm": 1.5,
    },
    "sections": [
        "title_page",
        "purpose",
        "flowchart",
        "listing",
        "test_results",
        "conclusion",
    ],
    "title_page": {
        "university": "Университет",
        "faculty": "Факультет",
        "department": "Кафедра",
        "discipline": "Программирование",
        "work_type": "Лабораторная работа",
    },
    "line_spacing": 1.5,
    "page_numbers": True,
}


def get_profiles_dir():
    """Возвращает абсолютный путь к директории профилей.

    Returns:
        Строка с путём к директории.
    """
    profiles_dir = os.path.abspath(PROFILES_DIR)
    os.makedirs(profiles_dir, exist_ok=True)
    return profiles_dir


def list_profiles():
    """Возвращает список доступных профилей.

    Returns:
        Список имён профилей (без расширения).
    """
    profiles_dir = get_profiles_dir()
    profiles = ["default"]

    for f in os.listdir(profiles_dir):
        if f.endswith(".json"):
            name = os.path.splitext(f)[0]
            if name not in profiles:
                profiles.append(name)

    return profiles


def load_profile(name="default"):
    """Загружает профиль преподавателя.

    Args:
        name: Имя профиля. 'default' для стандартного.

    Returns:
        Словарь с настройками профиля.
    """
    if name == "default":
        return DEFAULT_PROFILE.copy()

    profiles_dir = get_profiles_dir()
    filepath = os.path.join(profiles_dir, f"{name}.json")

    if not os.path.exists(filepath):
        return DEFAULT_PROFILE.copy()

    with open(filepath, "r", encoding="utf-8") as f:
        profile = json.load(f)

    # Дополняем недостающие поля из профиля по умолчанию
    merged = DEFAULT_PROFILE.copy()
    merged.update(profile)
    return merged


def save_profile(name, profile_data):
    """Сохраняет профиль преподавателя.

    Args:
        name: Имя профиля.
        profile_data: Словарь с настройками.
    """
    profiles_dir = get_profiles_dir()
    filepath = os.path.join(profiles_dir, f"{name}.json")

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(profile_data, f, ensure_ascii=False, indent=2)


def delete_profile(name):
    """Удаляет профиль преподавателя.

    Args:
        name: Имя профиля.

    Returns:
        True если профиль был удалён, False если не найден.
    """
    if name == "default":
        return False

    profiles_dir = get_profiles_dir()
    filepath = os.path.join(profiles_dir, f"{name}.json")

    if os.path.exists(filepath):
        os.remove(filepath)
        return True
    return False
