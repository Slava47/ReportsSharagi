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
from .flowchart import generate_flowchart, generate_mermaid_code, save_mermaid_code
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
        self.root.geometry("700x800")
        self.root.minsize(600, 700)

        self._create_widgets()

    def _create_widgets(self):
        """Создает виджеты интерфейса."""
        main_frame = ttk.Frame(self.root, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # --- Файлы заданий ---
        file_frame = ttk.LabelFrame(
            main_frame, text="Файлы заданий с исходным кодом", padding=5
        )
        file_frame.pack(fill=tk.X, pady=(0, 5))

        # Список файлов
        self.files_list = []  # list of (path, label)
        self.files_listbox = tk.Listbox(file_frame, height=4)
        self.files_listbox.pack(fill=tk.X, pady=(0, 5))

        btn_row = ttk.Frame(file_frame)
        btn_row.pack(fill=tk.X)
        ttk.Button(btn_row, text="Добавить файл...", command=self._add_file).pack(
            side=tk.LEFT, padx=(0, 5)
        )
        ttk.Button(btn_row, text="Удалить выбранный", command=self._remove_file).pack(
            side=tk.LEFT, padx=(0, 5)
        )

        label_row = ttk.Frame(file_frame)
        label_row.pack(fill=tk.X, pady=(5, 0))
        ttk.Label(label_row, text="Подпись:").pack(side=tk.LEFT)
        self.file_label_var = tk.StringVar()
        ttk.Entry(label_row, textvariable=self.file_label_var, width=30).pack(
            side=tk.LEFT, padx=5
        )
        ttk.Button(
            label_row, text="Обновить подпись",
            command=self._update_file_label
        ).pack(side=tk.LEFT)

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

        # --- Университет / Факультет / Кафедра ---
        uni_frame = ttk.LabelFrame(
            main_frame, text="Учебное заведение", padding=5
        )
        uni_frame.pack(fill=tk.X, pady=(0, 5))

        row_u = ttk.Frame(uni_frame)
        row_u.pack(fill=tk.X, pady=2)
        ttk.Label(row_u, text="Университет:").pack(side=tk.LEFT)
        self.university_var = tk.StringVar()
        ttk.Entry(row_u, textvariable=self.university_var).pack(
            side=tk.LEFT, fill=tk.X, expand=True, padx=5
        )

        row_f = ttk.Frame(uni_frame)
        row_f.pack(fill=tk.X, pady=2)
        ttk.Label(row_f, text="Факультет:").pack(side=tk.LEFT)
        self.faculty_var = tk.StringVar()
        ttk.Entry(row_f, textvariable=self.faculty_var).pack(
            side=tk.LEFT, fill=tk.X, expand=True, padx=5
        )

        row_d = ttk.Frame(uni_frame)
        row_d.pack(fill=tk.X, pady=2)
        ttk.Label(row_d, text="Кафедра:").pack(side=tk.LEFT)
        self.department_var = tk.StringVar()
        ttk.Entry(row_d, textvariable=self.department_var).pack(
            side=tk.LEFT, fill=tk.X, expand=True, padx=5
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

    def _add_file(self):
        """Открывает диалог выбора файла и добавляет в список."""
        filetypes = [
            ("Исходный код", "*.pas *.py *.cpp *.cc *.cxx *.c"),
            ("Pascal", "*.pas"),
            ("Python", "*.py"),
            ("C++", "*.cpp *.cc *.cxx *.c"),
            ("Все файлы", "*.*"),
        ]
        filepaths = filedialog.askopenfilenames(filetypes=filetypes)
        for filepath in filepaths:
            if filepath:
                self.files_list.append({"path": filepath, "label": ""})
                self.files_listbox.insert(tk.END, os.path.basename(filepath))

    def _remove_file(self):
        """Удаляет выбранный файл из списка."""
        selection = self.files_listbox.curselection()
        if selection:
            idx = selection[0]
            self.files_listbox.delete(idx)
            self.files_list.pop(idx)

    def _update_file_label(self):
        """Обновляет подпись выбранного файла."""
        selection = self.files_listbox.curselection()
        if not selection:
            messagebox.showwarning("Внимание", "Выберите файл из списка")
            return
        idx = selection[0]
        label = self.file_label_var.get().strip()
        self.files_list[idx]["label"] = label
        display = os.path.basename(self.files_list[idx]["path"])
        if label:
            display += f" [{label}]"
        self.files_listbox.delete(idx)
        self.files_listbox.insert(idx, display)

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
        if not self.files_list:
            messagebox.showerror("Ошибка", "Добавьте хотя бы один файл с исходным кодом")
            return

        for entry in self.files_list:
            if not os.path.exists(entry["path"]):
                messagebox.showerror(
                    "Ошибка", f"Файл не найден: {entry['path']}"
                )
                return

        self.generate_btn.config(state=tk.DISABLED)
        self.status_var.set("Генерация отчета...")

        thread = threading.Thread(target=self._do_generate, daemon=True)
        thread.start()

    def _do_generate(self):
        """Выполняет генерацию отчета (в отдельном потоке)."""
        try:
            source_file = self.files_list[0]["path"]

            # 1. Анализ всех файлов
            analyses = []
            for entry in self.files_list:
                fpath = entry["path"]
                self.root.after(0, self._log, f"Анализ файла: {fpath}")
                analysis = analyze_code(fpath)
                analysis["task_label"] = entry.get("label", "")
                self.root.after(
                    0, self._log,
                    f"  Язык: {analysis['language_display']}"
                )
                analyses.append(analysis)

            analysis = analyses[0]

            # 2. Тесты (для основного файла)
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

            # 3. Блок-схемы для всех файлов
            flowchart_paths = []
            mermaid_codes = []
            for a in analyses:
                self.root.after(
                    0, self._log,
                    f"Генерация блок-схемы для {a['filename']}..."
                )
                fc_path = generate_flowchart(a["code"], a["language"])
                mermaid = generate_mermaid_code(a["code"], a["language"])
                flowchart_paths.append(fc_path)
                mermaid_codes.append(mermaid)

            # 4. Отчет
            self.root.after(0, self._log, "Создание отчета...")
            student_info = {
                "name": self.name_var.get(),
                "group": self.group_var.get(),
                "variant": self.variant_var.get(),
            }

            # Переопределение полей титульной страницы
            title_overrides = {}
            uni = self.university_var.get().strip()
            fac = self.faculty_var.get().strip()
            dep = self.department_var.get().strip()
            if uni:
                title_overrides["university"] = uni
            if fac:
                title_overrides["faculty"] = fac
            if dep:
                title_overrides["department"] = dep

            # Дополнительные задания
            extra_tasks = []
            for i in range(1, len(analyses)):
                extra_tasks.append({
                    "analysis": analyses[i],
                    "flowchart_path": (
                        flowchart_paths[i] if i < len(flowchart_paths) else None
                    ),
                })

            output_path = generate_report(
                analysis=analysis,
                test_results=test_results,
                flowchart_path=flowchart_paths[0] if flowchart_paths else None,
                student_info=student_info,
                profile_name=self.profile_var.get(),
                title_overrides=title_overrides,
                extra_tasks=extra_tasks,
            )

            # 5. Сохраняем Mermaid-код рядом с отчетом
            for i, mermaid in enumerate(mermaid_codes):
                if mermaid:
                    base = os.path.splitext(output_path)[0]
                    suffix = "" if i == 0 else f"_task{i+1}"
                    mmd_path = f"{base}{suffix}_flowchart.mmd"
                    save_mermaid_code(mermaid, mmd_path)
                    self.root.after(
                        0, self._log, f"  Mermaid-код: {mmd_path}"
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
