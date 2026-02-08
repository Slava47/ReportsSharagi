"""Модуль выполнения кода.

Компилирует и запускает программы на Pascal, Python и C++
с заданными тестовыми данными.
"""

import os
import shutil
import subprocess
import tempfile


# Таймаут выполнения программы (секунды)
DEFAULT_TIMEOUT = 30


def _find_compiler(language):
    """Находит компилятор/интерпретатор для языка.

    Args:
        language: Язык программирования.

    Returns:
        Путь к компилятору или None.
    """
    compilers = {
        "pascal": ["pabcnetc", "fpc"],
        "python": ["python3", "python"],
        "cpp": ["g++", "gcc"],
    }

    for compiler in compilers.get(language, []):
        path = shutil.which(compiler)
        if path:
            return path
    return None


def _compile_pascal(source_path, compiler):
    """Компилирует файл Pascal.

    Args:
        source_path: Путь к исходному файлу.
        compiler: Путь к компилятору.

    Returns:
        Кортеж (путь к исполняемому файлу, сообщение об ошибке или None).
    """
    output_path = os.path.splitext(source_path)[0]
    try:
        result = subprocess.run(
            [compiler, source_path],
            capture_output=True,
            text=True,
            timeout=DEFAULT_TIMEOUT,
        )
        if result.returncode != 0:
            return None, result.stderr or result.stdout
        # fpc создает исполняемый файл без расширения
        if os.path.exists(output_path):
            return output_path, None
        return None, "Исполняемый файл не найден после компиляции"
    except subprocess.TimeoutExpired:
        return None, "Превышено время компиляции"
    except FileNotFoundError:
        return None, f"Компилятор не найден: {compiler}"


def _compile_cpp(source_path, compiler):
    """Компилирует файл C++.

    Args:
        source_path: Путь к исходному файлу.
        compiler: Путь к компилятору.

    Returns:
        Кортеж (путь к исполняемому файлу, сообщение об ошибке или None).
    """
    output_path = os.path.splitext(source_path)[0]
    try:
        result = subprocess.run(
            [compiler, source_path, "-o", output_path],
            capture_output=True,
            text=True,
            timeout=DEFAULT_TIMEOUT,
        )
        if result.returncode != 0:
            return None, result.stderr or result.stdout
        return output_path, None
    except subprocess.TimeoutExpired:
        return None, "Превышено время компиляции"
    except FileNotFoundError:
        return None, f"Компилятор не найден: {compiler}"


def compile_code(source_path, language):
    """Компилирует исходный код (для Pascal и C++).

    Args:
        source_path: Путь к файлу с исходным кодом.
        language: Язык программирования.

    Returns:
        Кортеж (путь к исполняемому файлу, сообщение об ошибке или None).
        Для Python возвращает (source_path, None).
    """
    if language == "python":
        return source_path, None

    compiler = _find_compiler(language)
    if compiler is None:
        return None, f"Компилятор для {language} не найден"

    if language == "pascal":
        return _compile_pascal(source_path, compiler)
    elif language == "cpp":
        return _compile_cpp(source_path, compiler)

    return None, f"Неподдерживаемый язык: {language}"


def run_program(executable_path, language, input_data="", timeout=None):
    """Запускает программу с тестовыми данными.

    Args:
        executable_path: Путь к исполняемому файлу.
        language: Язык программирования.
        input_data: Входные данные для программы.
        timeout: Таймаут выполнения в секундах.

    Returns:
        Словарь с результатами:
        - stdout: стандартный вывод
        - stderr: стандартный поток ошибок
        - returncode: код возврата
        - error: сообщение об ошибке или None
    """
    if timeout is None:
        timeout = DEFAULT_TIMEOUT

    if language == "python":
        cmd = [_find_compiler("python") or "python3", executable_path]
    else:
        cmd = [executable_path]

    try:
        result = subprocess.run(
            cmd,
            input=input_data,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        return {
            "stdout": result.stdout,
            "stderr": result.stderr,
            "returncode": result.returncode,
            "error": None,
        }
    except subprocess.TimeoutExpired:
        return {
            "stdout": "",
            "stderr": "",
            "returncode": -1,
            "error": f"Превышено время выполнения ({timeout} сек.)",
        }
    except FileNotFoundError:
        return {
            "stdout": "",
            "stderr": "",
            "returncode": -1,
            "error": f"Не удалось запустить: {executable_path}",
        }
    except PermissionError:
        return {
            "stdout": "",
            "stderr": "",
            "returncode": -1,
            "error": f"Нет прав на выполнение: {executable_path}",
        }


def run_tests(source_path, language, test_cases):
    """Запускает программу с несколькими тестовыми наборами данных.

    Args:
        source_path: Путь к файлу с исходным кодом.
        language: Язык программирования.
        test_cases: Список строк с входными данными.

    Returns:
        Словарь с результатами:
        - compiled: удалось ли скомпилировать
        - compile_error: ошибка компиляции или None
        - results: список результатов запуска для каждого теста
    """
    # Копируем исходный код во временную директорию для компиляции
    with tempfile.TemporaryDirectory() as tmpdir:
        ext = os.path.splitext(source_path)[1]
        tmp_source = os.path.join(tmpdir, f"program{ext}")
        with open(source_path, "r", encoding="utf-8") as src:
            code = src.read()
        with open(tmp_source, "w", encoding="utf-8") as dst:
            dst.write(code)

        executable, compile_error = compile_code(tmp_source, language)

        if compile_error:
            return {
                "compiled": False,
                "compile_error": compile_error,
                "results": [],
            }

        results = []
        for i, test_input in enumerate(test_cases):
            result = run_program(executable, language, test_input)
            result["test_number"] = i + 1
            result["input"] = test_input
            results.append(result)

        return {
            "compiled": True,
            "compile_error": None,
            "results": results,
        }
