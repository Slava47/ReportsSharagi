"""Графический интерфейс (GUI) для CodeLab Assistant.

Простое окно на tkinter для генерации отчетов.
"""

import os
import sys
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, ttk

from .analyzer import analyze_code
from .executor import run_tests
from .flowchart import generate_flowchart
from .profiles import list_profiles
from .report_generator import generate_report


class CodelabGUI:
    """Главное окно приложения."""

    def __init__(self, root):
        """Инициализация GUI.

        Args:
            root: Корневой элемент tkinter.
        """
        self.root = root
        self.root.title("CodeLab Assistant — Генератор отчетов")
        self.root.geometry("700x600")
        self.root.minsize(600, 500)

        self._create_widgets()

    def _create_widgets(self):
        """Создает виджеты интерфейса."""
        main_frame = ttk.Frame(self.root, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # --- Файл с кодом ---
        file_frame = ttk.LabelFrame(main_frame, text="Файл с исходным кодом", padding=5)
        file_frame.pack(fill=tk.X, pady=(0, 5))

        self.file_path_var = tk.StringVar()
        ttk.Entry(file_frame, textvariable=self.file_path_var).pack(
            side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5)
        )
        ttk.Button(file_frame, text="Обзор...", command=self._browse_file).pack(
            side=tk.RIGHT
        )

        # --- Данные студента ---
        student_frame = ttk.LabelFrame(main_frame, text="Данные студента", padding=5)
        student_frame.pack(fill=tk.X, pady=(0, 5))

        row1 = ttk.Frame(student_frame)
        row1.pack(fill=tk.X, pady=2)
        ttk.Label(row1, text="ФИО:").pack(side=tk.LEFT)
        self.name_var = tk.StringVar(value="Студент")
        ttk.Entry(row1, textvariable=self.name_var).pack(
            side=tk.LEFT, fill=tk.X, expand=True, padx=5
        )

        row2 = ttk.Frame(student_frame)
        row2.pack(fill=tk.X, pady=2)
        ttk.Label(row2, text="Группа:").pack(side=tk.LEFT)
        self.group_var = tk.StringVar()
        ttk.Entry(row2, textvariable=self.group_var, width=15).pack(
            side=tk.LEFT, padx=5
        )
        ttk.Label(row2, text="Вариант:").pack(side=tk.LEFT, padx=(10, 0))
        self.variant_var = tk.StringVar()
        ttk.Entry(row2, textvariable=self.variant_var, width=10).pack(
            side=tk.LEFT, padx=5
        )

        # --- Профиль ---
        profile_frame = ttk.Frame(main_frame)
        profile_frame.pack(fill=tk.X, pady=(0, 5))

        ttk.Label(profile_frame, text="Профиль:").pack(side=tk.LEFT)
        self.profile_var = tk.StringVar(value="default")
        profiles = list_profiles()
        self.profile_combo = ttk.Combobox(
            profile_frame, textvariable=self.profile_var,
            values=profiles, state="readonly", width=20
        )
        self.profile_combo.pack(side=tk.LEFT, padx=5)

        # --- Тестовые данные ---
        test_frame = ttk.LabelFrame(
            main_frame, text="Тестовые данные (разделяйте тесты строкой ---)",
            padding=5
        )
        test_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 5))

        self.test_data_text = scrolledtext.ScrolledText(test_frame, height=6)
        self.test_data_text.pack(fill=tk.BOTH, expand=True)

        # --- Кнопка генерации ---
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, pady=5)

        self.generate_btn = ttk.Button(
            btn_frame, text="Сгенерировать отчет",
            command=self._generate_report
        )
        self.generate_btn.pack(side=tk.LEFT, padx=(0, 10))

        self.status_var = tk.StringVar(value="Готов к работе")
        ttk.Label(btn_frame, textvariable=self.status_var).pack(
            side=tk.LEFT, fill=tk.X, expand=True
        )

        # --- Лог ---
        log_frame = ttk.LabelFrame(main_frame, text="Журнал", padding=5)
        log_frame.pack(fill=tk.BOTH, expand=True)

        self.log_text = scrolledtext.ScrolledText(log_frame, height=8, state=tk.DISABLED)
        self.log_text.pack(fill=tk.BOTH, expand=True)

    def _browse_file(self):
        """Открывает диалог выбора файла."""
        filetypes = [
            ("Исходный код", "*.pas *.py *.cpp *.cc *.cxx *.c"),
            ("Pascal", "*.pas"),
            ("Python", "*.py"),
            ("C++", "*.cpp *.cc *.cxx *.c"),
            ("Все файлы", "*.*"),
        ]
        filepath = filedialog.askopenfilename(filetypes=filetypes)
        if filepath:
            self.file_path_var.set(filepath)

    def _log(self, message):
        """Добавляет сообщение в журнал.

        Args:
            message: Текст сообщения.
        """
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)

    def _generate_report(self):
        """Запускает генерацию отчета в отдельном потоке."""
        source_file = self.file_path_var.get()

        if not source_file or not os.path.exists(source_file):
            messagebox.showerror("Ошибка", "Выберите файл с исходным кодом")
            return

        self.generate_btn.config(state=tk.DISABLED)
        self.status_var.set("Генерация отчета...")

        thread = threading.Thread(target=self._do_generate, daemon=True)
        thread.start()

    def _do_generate(self):
        """Выполняет генерацию отчета (в отдельном потоке)."""
        try:
            source_file = self.file_path_var.get()

            # 1. Анализ
            self.root.after(0, self._log, f"Анализ файла: {source_file}")
            analysis = analyze_code(source_file)
            self.root.after(0, self._log,
                            f"  Язык: {analysis['language_display']}")

            # 2. Тесты
            test_data_raw = self.test_data_text.get("1.0", tk.END).strip()
            test_results = None

            if test_data_raw:
                test_cases = [
                    t.strip() for t in test_data_raw.split("---") if t.strip()
                ]
                self.root.after(0, self._log,
                                f"Запуск {len(test_cases)} тестов...")
                test_results = run_tests(
                    source_file, analysis["language"], test_cases
                )
                if test_results["compiled"]:
                    for r in test_results["results"]:
                        status = "✓" if r["returncode"] == 0 else "✗"
                        self.root.after(
                            0, self._log,
                            f"  Тест {r['test_number']}: {status}"
                        )

            # 3. Блок-схема
            self.root.after(0, self._log, "Генерация блок-схемы...")
            flowchart_path = generate_flowchart(
                analysis["code"], analysis["language"]
            )

            # 4. Отчет
            self.root.after(0, self._log, "Создание отчета...")
            student_info = {
                "name": self.name_var.get(),
                "group": self.group_var.get(),
                "variant": self.variant_var.get(),
            }

            output_path = generate_report(
                analysis=analysis,
                test_results=test_results,
                flowchart_path=flowchart_path,
                student_info=student_info,
                profile_name=self.profile_var.get(),
            )

            self.root.after(0, self._log, f"Отчет сохранен: {output_path}")
            self.root.after(0, self.status_var.set, "Готово!")
            self.root.after(
                0, messagebox.showinfo,
                "Готово", f"Отчет сохранен:\n{output_path}"
            )

        except Exception as e:
            self.root.after(0, self._log, f"Ошибка: {e}")
            self.root.after(0, self.status_var.set, "Ошибка!")
            self.root.after(
                0, messagebox.showerror, "Ошибка", str(e)
            )

        finally:
            self.root.after(0, self.generate_btn.config, {"state": tk.NORMAL})


def main():
    """Запускает графический интерфейс."""
    root = tk.Tk()
    CodelabGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
