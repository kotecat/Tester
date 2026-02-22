import sqlite3
import tkinter as tk
import tkinter.font as tkFont
from tkinter import ttk

from config import DB_NAME
from database.db import get_connection, init_db
from database.repo import TestRepository, QuestionRepository, AnswerRepository, ResultRepository

from windows.test_runner import TestRunnerMixin
from windows.test_manager import TestManagerMixin
from windows.results_view import ResultsViewMixin


BG_MAIN = "#f6e9ff"
BG_FRAME = "#f0ddff"
FG_TEXT = "#2d123d"
ACCENT = "#c39bff"


def center_window(win, width=900, height=600):
    win.update_idletasks()
    screen_width = win.winfo_screenwidth()
    screen_height = win.winfo_screenheight()
    x = (screen_width - width) // 2
    y = (screen_height - height) // 2
    win.geometry(f"{width}x{height}+{x}+{y}")


class App(tk.Tk, TestRunnerMixin, TestManagerMixin, ResultsViewMixin):
    def __init__(self):
        tk.Tk.__init__(self)
        self.title("TesterMaker")
        self.configure(bg=BG_MAIN)
        center_window(self, 900, 600)

        self.base_font_size = 12
        self.ui_font = tkFont.Font(family="Segoe UI", size=self.base_font_size)
        self.header_font = tkFont.Font(family="Segoe UI", size=self.base_font_size + 4, weight="bold")
        self.title_font = tkFont.Font(family="Segoe UI", size=self.base_font_size + 8, weight="bold")

        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure(
            "Modern.TButton",
            font=self.ui_font,
            padding=(10, 6),
            relief="flat",
            background=ACCENT,
            foreground=FG_TEXT,
            borderwidth=0,
        )
        style.map(
            "Modern.TButton",
            background=[("active", "#b08bff"), ("disabled", "#d8c7ff")],
        )
        style.configure("Modern.TFrame", background=BG_FRAME)
        style.configure("Modern.TLabel", background=BG_FRAME, foreground=FG_TEXT, font=self.ui_font)
        style.configure("Modern.Treeview", background="white", fieldbackground="white", foreground=FG_TEXT, font=self.ui_font)
        style.configure("Modern.Treeview.Heading", font=self.ui_font)

        self.conn: sqlite3.Connection = get_connection(DB_NAME)
        init_db(self.conn)
        self.tests_repo = TestRepository(self.conn)
        self.questions_repo = QuestionRepository(self.conn)
        self.answers_repo = AnswerRepository(self.conn)
        self.results_repo = ResultRepository(self.conn)

        self.BG_MAIN = BG_MAIN
        self.BG_FRAME = BG_FRAME
        self.FG_TEXT = FG_TEXT
        self.ACCENT = ACCENT
        self.center_window = center_window

        self.user_name: str = ""
        self.group_name: str = ""

        self.show_main_menu()


    def clear_root(self):
        for w in self.winfo_children():
            w.destroy()

    def make_frame(self):
        frame = ttk.Frame(self, style="Modern.TFrame")
        frame.pack(padx=20, pady=20, fill="both", expand=True)
        return frame

    def set_fullscreen(self, on: bool):
        self.attributes("-fullscreen", on)

    def show_main_menu(self):
        self.timer_running = False if hasattr(self, "timer_running") else False
        self.set_fullscreen(False)
        self.clear_root()
        center_window(self, 700, 500)

        frame = self.make_frame()

        ttk.Label(
            frame,
            text="TesterMaker - Система тестирования",
            font=self.title_font,
            style="Modern.TLabel",
        ).pack(pady=(10, 20))

        btn_width = 24

        ttk.Button(
            frame,
            text="Начать тестирование",
            command=self.start_testing_menu,
            style="Modern.TButton",
            width=btn_width,
        ).pack(pady=5)

        ttk.Button(
            frame,
            text="Менеджер тестов",
            command=self.show_test_manager,
            style="Modern.TButton",
            width=btn_width,
        ).pack(pady=5)

        ttk.Button(
            frame,
            text="Ведомость (результаты)",
            command=self.show_results_view,
            style="Modern.TButton",
            width=btn_width,
        ).pack(pady=5)

        ttk.Button(
            frame,
            text="Выход",
            command=self.on_close,
            style="Modern.TButton",
            width=btn_width,
        ).pack(pady=(20, 10))

    def on_close(self):
        if hasattr(self, "timer_running"):
            self.timer_running = False
        if self.conn:
            self.conn.close()
        self.destroy()


if __name__ == "__main__":
    app = App()
    app.protocol("WM_DELETE_WINDOW", app.on_close)
    app.mainloop()
