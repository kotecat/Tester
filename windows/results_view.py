import tkinter as tk
from tkinter import ttk
from dateutil import tz
from datetime import datetime

from database.models import Result


class ResultsViewMixin:
    def show_results_view(self):
        self.set_fullscreen(False)
        self.clear_root()
        self.center_window(self, 1000, 650)

        frame = self.make_frame()

        ttk.Label(
            frame,
            text="Ведомость результатов",
            font=self.header_font,
            style="Modern.TLabel",
        ).pack(anchor="w", pady=(10, 10))

        top = ttk.Frame(frame, style="Modern.TFrame")
        top.pack(fill="x")

        ttk.Label(
            top,
            text="Тест:",
            style="Modern.TLabel",
        ).pack(side="left")

        self.results_test_var = tk.StringVar()
        self.results_groups_var = tk.StringVar()
        
        self.results_tests_combo = ttk.Combobox(
            top, textvariable=self.results_test_var, state="readonly", font=self.ui_font
        )
        self.results_tests_combo.pack(side="left", padx=(5, 5), fill="x", expand=True)

        self.results_tests = self.tests_repo.find_all(limit=1000)
        names = [t.name for t in self.results_tests]
        self.results_tests_combo["values"] = names
        if names:
            self.results_tests_combo.current(0)
            self.results_tests_combo.bind(
                "<<ComboboxSelected>>",
                lambda e: self.load_results_table(),
            )

        ttk.Button(
            top,
            text="Обновить",
            command=self.load_results_table,
            style="Modern.TButton",
            width=10,
        ).pack(side="left", padx=(5, 0))

        columns = (
            "user_name",
            "group_name",
            "score",
            "percent",
            "time_taken",
            "taken_at",
        )
        self.results_tree = ttk.Treeview(
            frame, columns=columns, show="headings", height=18, style="Modern.Treeview"
        )
        self.results_tree.heading("user_name", text="Имя")
        self.results_tree.heading("group_name", text="Группа")
        self.results_tree.heading("score", text="Баллы")
        self.results_tree.heading("percent", text="%")
        self.results_tree.heading("time_taken", text="Время (с)")
        self.results_tree.heading("taken_at", text="Дата завершения")

        self.results_tree.column("user_name", width=150)
        self.results_tree.column("group_name", width=120)
        self.results_tree.column("score", width=90, anchor="center")
        self.results_tree.column("percent", width=70, anchor="center")
        self.results_tree.column("time_taken", width=90, anchor="center")
        self.results_tree.column("taken_at", width=180)

        self.results_tree.pack(fill="both", expand=True, pady=(10, 10))

        ttk.Button(
            frame,
            text="Назад",
            command=self.show_main_menu,
            style="Modern.TButton",
            width=12,
        ).pack(anchor="e", pady=(0, 10))
        
        self.load_results_table()

    def load_results_table(self, *args):
        for row in self.results_tree.get_children():
            self.results_tree.delete(row)

        name = self.results_test_var.get()
        test_obj = next((t for t in self.results_tests if t.name == name), None)
        if not test_obj:
            return

        results: list[Result] = self.results_repo.find_by_test(test_obj.id)
        for r in results:
            percent = 0.0
            if r.max_score:
                percent = round(r.score * 100.0 / r.max_score, 1)
            taken_at = datetime.fromisoformat(r.taken_at) if r.taken_at else None
            if taken_at:
                taken_at = (
                    taken_at
                    .replace(tzinfo=tz.UTC)
                    .astimezone(tz.tzlocal())
                    .strftime("%Y-%m-%d %H:%M:%S")
                )
            self.results_tree.insert(
                "",
                "end",
                values=(
                    r.user_name,
                    r.group_name or "",
                    f"{r.score}/{r.max_score}",
                    percent,
                    r.time_taken,
                    str(taken_at or ""),
                ),
            )
