import time
import threading
import tkinter as tk
import tkinter.font as tkFont
from tkinter import ttk, messagebox
from tkinter.simpledialog import askstring, askinteger
from datetime import timedelta


class TestRunnerMixin:
    def ask_user_info(self):
        """Окно с полями Имя и Группа в одном диалоге."""
        dialog = tk.Toplevel(self)
        dialog.title("Данные тестируемого")
        dialog.transient(self)
        dialog.grab_set()
        dialog.configure(bg=self.BG_FRAME)

        self.center_window(dialog, 400, 200)

        name_var = tk.StringVar()
        group_var = tk.StringVar()

        frame = ttk.Frame(dialog, style="Modern.TFrame")
        frame.pack(fill="both", expand=True, padx=15, pady=15)

        ttk.Label(frame, text="Имя:", style="Modern.TLabel").pack(anchor="w")
        name_entry = ttk.Entry(frame, textvariable=name_var, font=self.ui_font)
        name_entry.pack(fill="x", pady=(0, 10))

        ttk.Label(frame, text="Группа:", style="Modern.TLabel").pack(anchor="w")
        group_entry = ttk.Entry(frame, textvariable=group_var, font=self.ui_font)
        group_entry.pack(fill="x", pady=(0, 10))

        btn_frame = ttk.Frame(frame, style="Modern.TFrame")
        btn_frame.pack(fill="x", pady=(10, 0))

        def on_ok():
            if not name_var.get().strip():
                messagebox.showwarning("Имя", "Введите имя.")
                return
            dialog.destroy()

        def on_cancel():
            name_var.set("")
            dialog.destroy()

        ttk.Button(
            btn_frame,
            text="Отмена",
            command=on_cancel,
            style="Modern.TButton",
            width=10,
        ).pack(side="right")
        ttk.Button(
            btn_frame,
            text="OK",
            command=on_ok,
            style="Modern.TButton",
            width=10,
        ).pack(side="right", padx=(0, 5))

        name_entry.focus_set()
        self.wait_window(dialog)

        name = name_var.get().strip()
        group = group_var.get().strip()
        if not name:
            return None, None
        return name, group

    def start_testing_menu(self):
        # вместо двух askstring вызываем один диалог
        name, group = self.ask_user_info()
        if not name:
            return

        self.user_name = name
        self.group_name = group

        self.clear_root()
        frame = self.make_frame()

        ttk.Label(
            frame,
            text=f"Тестируемый: {self.user_name} ({self.group_name})",
            style="Modern.TLabel",
        ).pack(anchor="w", pady=(10, 10))

        ttk.Label(
            frame,
            text="Выбор теста",
            font=self.header_font,
            style="Modern.TLabel",
        ).pack(anchor="w", pady=(0, 10))

        list_frame = ttk.Frame(frame, style="Modern.TFrame")
        list_frame.pack(fill="both", expand=True)

        self.tests_list = tk.Listbox(
            list_frame,
            height=15,
            bg="white",
            fg=self.FG_TEXT,
            selectbackground=self.ACCENT,
            font=self.ui_font,
            bd=0,
            highlightthickness=1,
            highlightbackground="#d0c0ff",
        )
        self.tests_list.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.tests_list.yview)
        scrollbar.pack(side="right", fill="y")
        self.tests_list.config(yscrollcommand=scrollbar.set)

        btn_frame = ttk.Frame(frame, style="Modern.TFrame")
        btn_frame.pack(fill="x", pady=(10, 0))

        ttk.Button(
            btn_frame,
            text="Обновить список",
            command=self.load_tests_into_list,
            style="Modern.TButton",
            width=18,
        ).pack(side="left", padx=(0, 5))
        ttk.Button(
            btn_frame,
            text="Начать выбранный тест",
            command=self.start_selected_test,
            style="Modern.TButton",
            width=22,
        ).pack(side="right")

        ttk.Button(
            frame,
            text="Назад",
            command=self.show_main_menu,
            style="Modern.TButton",
            width=12,
        ).pack(anchor="e", pady=(10, 10))

        self.load_tests_into_list()

    def load_tests_into_list(self):
        self.tests_list.delete(0, tk.END)
        self.tests_cache = self.tests_repo.find_all(limit=1000)
        for t in self.tests_cache:
            line = f"{t.name}  |  вопросов: {t.questions}, время: {t.time_limit} c"
            self.tests_list.insert(tk.END, line)

    def start_selected_test(self):
        sel = self.tests_list.curselection()
        if not sel:
            messagebox.showwarning("Тест", "Выберите тест.")
            return
        idx = sel[0]
        self.current_test = self.tests_cache[idx]

        all_questions = self.questions_repo.find_by_test(self.current_test.id)
        if not all_questions:
            messagebox.showinfo("Тест", "У этого теста пока нет вопросов.")
            return

        import random
        random.shuffle(all_questions)
        max_q = self.current_test.questions
        chosen_questions = all_questions[:max_q]

        self.current_questions = []
        for q in chosen_questions:
            answers = self.answers_repo.find_by_question(q.id)
            if not answers:
                continue
            random.shuffle(answers)
            self.current_questions.append((q, answers))

        if not self.current_questions:
            messagebox.showinfo("Тест", "Нет вопросов с ответами.")
            return

        self.current_index = 0
        self.current_score = 0
        self.max_score = len(self.current_questions)
        self.selected_answer = tk.IntVar(value=-1)
        self.answers_choice = [-1] * self.max_score

        self.time_left = self.current_test.time_limit
        self.timer_running = True
        self.test_start_time = time.time()

        self.question_font = tkFont.Font(family="Segoe UI", size=16)
        self.options_font = tkFont.Font(family="Segoe UI", size=14)
        self.timer_font = tkFont.Font(family="Segoe UI", size=14)
        self.scale_font = tkFont.Font(family="Segoe UI", size=10)

        self.set_fullscreen(True)
        self.bind_all("<Key>", self.on_key_pressed)

        self.show_question_screen()
        self.start_timer_thread()

    def on_key_pressed(self, event):
        if not getattr(self, "current_questions", None):
            return

        if event.char.isdigit():
            num = int(event.char)
            if 1 <= num <= len(self.current_questions[self.current_index][1]):
                self.selected_answer.set(num - 1)
                self.answers_choice[self.current_index] = num - 1
            return

        if event.keysym == "Return":
            if self.current_index < self.max_score - 1:
                self.next_question()
            else:
                self.finish_test()

    def show_question_screen(self):
        self.clear_root()
        frame = self.make_frame()

        top = ttk.Frame(frame, style="Modern.TFrame")
        top.pack(fill="x")

        ttk.Label(
            top,
            text=f"Тест: {self.current_test.name}",
            font=self.header_font,
            style="Modern.TLabel",
        ).pack(side="left")

        self.timer_label = ttk.Label(
            top,
            text=f"Осталось: {timedelta(seconds=int(self.time_left))}",
            style="Modern.TLabel",
            font=self.timer_font,
        )
        self.timer_label.pack(side="right", padx=(10, 0))

        scale_frame = ttk.Frame(frame, style="Modern.TFrame")
        scale_frame.pack(fill="x", pady=(5, 5))
        ttk.Label(
            scale_frame,
            text="Масштаб шрифта:",
            style="Modern.TLabel",
        ).pack(side="left")
        self.font_scale = tk.Scale(
            scale_frame,
            from_=12,
            to=28,
            orient="horizontal",
            command=self.update_font_scale,
            bg=self.BG_FRAME,
            fg=self.FG_TEXT,
            troughcolor="#e0cfff",
            highlightthickness=0,
            font=self.scale_font,
            length=200,
        )
        self.font_scale.set(self.question_font.cget("size"))
        self.font_scale.pack(side="left", padx=(5, 0))

        q_row, answers = self.current_questions[self.current_index]

        ttk.Label(
            frame,
            text=f"Вопрос {self.current_index + 1} из {len(self.current_questions)}",
            style="Modern.TLabel",
        ).pack(anchor="w", pady=(5, 5))

        self.question_label = tk.Label(
            frame,
            text=q_row.q_text,
            font=self.question_font,
            bg="#ffffff",
            fg=self.FG_TEXT,
            justify="left",
            wraplength=1100,
            bd=1,
            relief="solid",
        )
        self.question_label.pack(fill="x", padx=5, pady=(0, 10))

        self.options_frame = ttk.Frame(frame, style="Modern.TFrame")
        self.options_frame.pack(fill="both", expand=True)

        self.selected_answer.set(self.answers_choice[self.current_index])

        self.option_buttons = []
        for i, ans in enumerate(answers):
            rb = tk.Radiobutton(
                self.options_frame,
                text=ans.a_text,
                variable=self.selected_answer,
                value=i,
                anchor="w",
                justify="left",
                wraplength=1100,
                bg=self.BG_FRAME,
                fg=self.FG_TEXT,
                selectcolor="#e9d3ff",
                font=self.options_font,
                bd=0,
                highlightthickness=0,
            )
            rb.pack(fill="x", anchor="w", padx=10, pady=2)
            self.option_buttons.append(rb)

        nav_frame = ttk.Frame(frame, style="Modern.TFrame")
        nav_frame.pack(fill="x", pady=(10, 0))

        back_btn = ttk.Button(
            nav_frame,
            text="Назад",
            command=self.prev_question,
            style="Modern.TButton",
            width=10,
        )
        back_btn.pack(side="left")
        if self.current_index == 0:
            back_btn.config(state="disabled")

        next_btn = ttk.Button(
            nav_frame,
            text="Вперёд",
            command=self.next_question,
            style="Modern.TButton",
            width=10,
        )
        next_btn.pack(side="left", padx=5)
        if self.current_index >= self.max_score - 1:
            next_btn.config(state="disabled")

        ttk.Button(
            nav_frame,
            text="Завершить тест",
            command=self.finish_test,
            style="Modern.TButton",
            width=14,
        ).pack(side="right", padx=(5, 0))

        ttk.Button(
            nav_frame,
            text="Отмена теста",
            command=self.cancel_test,
            style="Modern.TButton",
            width=12,
        ).pack(side="right")

    def update_font_scale(self, value):
        size = int(float(value))
        self.question_font.config(size=size)
        self.timer_font.config(size=size)
        self.options_font.config(size=max(size - 2, 10))

    def start_timer_thread(self):
        def run_timer():
            while self.timer_running and self.time_left > 0:
                time.sleep(1)
                self.time_left -= 1
                self.after(0, self.update_timer_label)
            if self.timer_running and self.time_left <= 0:
                self.after(0, self.time_over)

        self.timer_thread = threading.Thread(target=run_timer, daemon=True)
        self.timer_thread.start()

    def update_timer_label(self):
        if hasattr(self, "timer_label"):
            time_left = timedelta(seconds=int(self.time_left))
            self.timer_label.config(text=f"Осталось: {time_left}")

    def time_over(self):
        messagebox.showinfo("Время", "Время теста вышло.\nРезультат будет сохранён.")
        self.finish_test()

    def save_current_answer(self):
        idx = self.selected_answer.get()
        self.answers_choice[self.current_index] = idx

    def prev_question(self):
        self.save_current_answer()
        if self.current_index > 0:
            self.current_index -= 1
            self.show_question_screen()

    def next_question(self):
        self.save_current_answer()
        if self.current_index < self.max_score - 1:
            self.current_index += 1
            self.show_question_screen()

    def finish_test(self):
        if not getattr(self, "current_questions", None):
            self.set_fullscreen(False)
            self.unbind_all("<Key>")
            self.show_main_menu()
            return

        self.timer_running = False
        self.save_current_answer()

        self.current_score = 0
        for i, (q_row, answers) in enumerate(self.current_questions):
            chosen_index = self.answers_choice[i]
            if chosen_index is None or chosen_index < 0:
                continue
            if answers[chosen_index].is_correct:
                self.current_score += 1

        total = self.max_score
        score = self.current_score
        time_taken = int(time.time() - self.test_start_time)

        self.results_repo.create(
            {
                "test_id": self.current_test.id,
                "user_name": self.user_name,
                "group_name": self.group_name,
                "score": score,
                "max_score": total,
                "time_taken": time_taken,
            }
        )

        self.set_fullscreen(False)
        self.unbind_all("<Key>")
        messagebox.showinfo(
            "Результат",
            f"Тест завершён.\nВаш результат: {score}/{total}\nВремя: {time_taken} с",
        )
        self.show_main_menu()

    def cancel_test(self):
        if not getattr(self, "current_questions", None):
            self.set_fullscreen(False)
            self.unbind_all("<Key>")
            self.show_main_menu()
            return
        self.timer_running = False
        if messagebox.askyesno("Отмена", "Вы действительно хотите прервать тест?"):
            self.set_fullscreen(False)
            self.unbind_all("<Key>")
            self.show_main_menu()
        else:
            self.timer_running = True
            self.start_timer_thread()
