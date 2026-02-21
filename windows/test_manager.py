import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from tkinter.simpledialog import askinteger
from datetime import timedelta


class TestManagerMixin:
    def show_test_manager(self):
        self.set_fullscreen(False)
        self.clear_root()
        self.center_window(self, 1000, 700)

        frame = self.make_frame()

        ttk.Label(
            frame,
            text="Менеджер тестов",
            font=self.header_font,
            style="Modern.TLabel",
        ).pack(anchor="w", pady=(10, 10))

        main_split = tk.PanedWindow(frame, orient="horizontal", sashrelief="raised", bg=self.BG_FRAME)
        main_split.pack(fill="both", expand=True)

        left = ttk.Frame(main_split, style="Modern.TFrame", padding=(0, 0, 10, 0))
        main_split.add(left, minsize=320)

        ttk.Label(
            left,
            text="Существующие тесты:",
            style="Modern.TLabel",
        ).pack(anchor="w")

        self.manager_tests_list = tk.Listbox(
            left,
            height=20,
            bg="white",
            fg=self.FG_TEXT,
            selectbackground=self.ACCENT,
            font=self.ui_font,
            bd=0,
            highlightthickness=1,
            highlightbackground="#d0c0ff",
        )
        self.manager_tests_list.pack(fill="both", expand=True, pady=(5, 5))

        m_scroll = ttk.Scrollbar(left, orient="vertical", command=self.manager_tests_list.yview)
        m_scroll.pack(side="right", fill="y")
        self.manager_tests_list.config(yscrollcommand=m_scroll.set)

        self.manager_tests_list.bind("<Double-Button-1>", self.on_test_double_click)

        btns_left = ttk.Frame(left, style="Modern.TFrame")
        btns_left.pack(fill="x", pady=(5, 0))

        ttk.Button(
            btns_left,
            text="Обновить",
            command=self.load_manager_tests,
            style="Modern.TButton",
            width=10,
        ).pack(side="left")

        ttk.Button(
            btns_left,
            text="Удалить",
            command=self.delete_selected_test,
            style="Modern.TButton",
            width=10,
        ).pack(side="right")

        right = ttk.Frame(main_split, style="Modern.TFrame", padding=(10, 0))
        main_split.add(right, minsize=420)

        ttk.Label(
            right,
            text="Создание / редактирование теста",
            style="Modern.TLabel",
        ).pack(anchor="w", pady=(0, 5))

        ttk.Label(right, text="Имя теста:", style="Modern.TLabel").pack(anchor="w")
        self.m_test_name = tk.StringVar()
        ttk.Entry(right, textvariable=self.m_test_name, font=self.ui_font).pack(fill="x", pady=(0, 5))

        ttk.Label(right, text="Описание теста:", style="Modern.TLabel").pack(anchor="w")
        self.m_test_desc = tk.StringVar()
        ttk.Entry(right, textvariable=self.m_test_desc, font=self.ui_font).pack(fill="x", pady=(0, 5))

        ttk.Label(
            right,
            text="Сколько вопросов брать случайно:",
            style="Modern.TLabel",
        ).pack(anchor="w")
        self.m_questions = tk.IntVar(value=10)
        ttk.Entry(right, textvariable=self.m_questions, font=self.ui_font).pack(fill="x", pady=(0, 5))

        ttk.Label(
            right,
            text="Лимит времени (секунды):",
            style="Modern.TLabel",
        ).pack(anchor="w")
        self.m_time_limit = tk.IntVar(value=300)
        ttk.Entry(right, textvariable=self.m_time_limit, font=self.ui_font).pack(fill="x", pady=(0, 10))

        btns_right_top = ttk.Frame(right, style="Modern.TFrame")
        btns_right_top.pack(fill="x", pady=(5, 0))

        self.btn_new_test = ttk.Button(
            btns_right_top,
            text="Создать новый",
            command=self.new_test_form,
            style="Modern.TButton",
            width=16,
        )
        self.btn_new_test.pack(side="left", padx=(0, 5))

        self.btn_save_edit = ttk.Button(
            btns_right_top,
            text="Сохранить изменения",
            command=self.save_edit_metadata,
            style="Modern.TButton",
            width=18,
        )
        self.btn_save_edit.pack(side="left", padx=(0, 5))

        btns_right_bottom = ttk.Frame(right, style="Modern.TFrame")
        btns_right_bottom.pack(fill="x", pady=(5, 0))

        ttk.Button(
            btns_right_bottom,
            text="Загрузить/обновить из TXT",
            command=self.load_or_update_test_from_txt,
            style="Modern.TButton",
            width=24,
        ).pack(side="left")

        ttk.Button(
            frame,
            text="Назад",
            command=self.show_main_menu,
            style="Modern.TButton",
            width=12,
        ).pack(anchor="e", pady=(10, 10))

        self.current_edit_test_id = None
        self.btn_save_edit.pack_forget()

        self.load_manager_tests()

    # ---------- helpers ----------

    def load_manager_tests(self):
        self.manager_tests_list.delete(0, tk.END)
        self.manager_tests = self.tests_repo.find_all(limit=1000)
        for t in self.manager_tests:
            self.manager_tests_list.insert(
                tk.END, f"[{t.id}] {t.name}  |  вопросов: {t.questions} | {timedelta(seconds=int(t.time_limit))}"
            )

    def get_selected_test(self):
        sel = self.manager_tests_list.curselection()
        if not sel:
            return None
        idx = sel[0]
        return self.manager_tests[idx]

    def new_test_form(self):
        """Режим создания нового теста: очищаем форму и скрываем 'Сохранить изменения'."""
        self.current_edit_test_id = None
        self.m_test_name.set("")
        self.m_test_desc.set("")
        self.m_questions.set(10)
        self.m_time_limit.set(300)
        if self.btn_save_edit.winfo_ismapped():
            self.btn_save_edit.pack_forget()

    def on_test_double_click(self, event):
        test_obj = self.get_selected_test()
        if not test_obj:
            return
        self.current_edit_test_id = test_obj.id
        self.m_test_name.set(test_obj.name)
        self.m_test_desc.set(test_obj.description or "")
        self.m_questions.set(test_obj.questions)
        self.m_time_limit.set(test_obj.time_limit)
        if not self.btn_save_edit.winfo_ismapped():
            self.btn_save_edit.pack(side="left", padx=(0, 5))

    def delete_selected_test(self):
        test_obj = self.get_selected_test()
        if not test_obj:
            messagebox.showwarning("Удаление", "Выберите тест.")
            return
        if not messagebox.askyesno(
            "Удаление", f"Удалить тест '{test_obj.name}' со всеми вопросами и результатами?"
        ):
            return
        self.tests_repo.delete(test_obj.id)
        if self.current_edit_test_id == test_obj.id:
            self.new_test_form()
        self.load_manager_tests()

    # ---------- сохранение ----------

    def save_edit_metadata(self):
        """Сохранить изменения в выбранном тесте по id, имя можно менять."""
        if self.current_edit_test_id is None:
            messagebox.showwarning(
                "Сохранение",
                "Выберите тест для редактирования (двойной клик по списку) или нажмите 'Создать новый'.",
            )
            return

        name = self.m_test_name.get().strip()
        if not name:
            messagebox.showwarning("Сохранение", "Заполните имя теста.")
            return

        desc = self.m_test_desc.get().strip() or None
        q_count = self.m_questions.get() or 1
        time_limit = self.m_time_limit.get() or 60

        self.conn.execute(
            "UPDATE tests SET name = ?, description = ?, questions = ?, time_limit = ? WHERE id = ?",
            (name, desc, q_count, time_limit, self.current_edit_test_id),
        )
        self.conn.commit()
        messagebox.showinfo("Сохранение", f"Метаданные теста '{name}' обновлены.")
        self.load_manager_tests()

    # ---------- загрузка/обновление из TXT ----------

    def load_or_update_test_from_txt(self):
        name_from_form = self.m_test_name.get().strip()
        if not name_from_form:
            messagebox.showwarning("Имя теста", "Заполните имя теста.")
            return

        path = filedialog.askopenfilename(
            title="Выберите TXT файл",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
        )
        if not path:
            return

        try:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось прочитать файл:\n{e}")
            return

        blocks = [b.strip() for b in content.split("<question>") if b.strip()]
        if not blocks:
            messagebox.showwarning("Файл", "Не найдено ни одного вопроса.")
            return

        if self.m_questions.get():
            questions_count = self.m_questions.get()
        else:
            questions_count = askinteger(
                "Количество вопросов",
                "Сколько вопросов выбирать случайным образом при тестировании?",
                minvalue=1,
                initialvalue=len(blocks),
            )
            if not questions_count:
                return
            self.m_questions.set(questions_count)

        desc = self.m_test_desc.get().strip() or None
        time_limit = self.m_time_limit.get() or 60

        if self.current_edit_test_id is not None:
            test_id = self.current_edit_test_id
            self.conn.execute(
                "DELETE FROM answers WHERE question_id IN (SELECT id FROM questions WHERE test_id = ?)",
                (test_id,),
            )
            self.conn.execute("DELETE FROM questions WHERE test_id = ?", (test_id,))
            self.conn.execute(
                "UPDATE tests SET name = ?, description = ?, questions = ?, time_limit = ? WHERE id = ?",
                (name_from_form, desc, questions_count, time_limit, test_id),
            )
            self.conn.commit()
        else:
            test_obj = self.tests_repo.create(
                {
                    "name": name_from_form,
                    "description": desc,
                    "questions": questions_count,
                    "time_limit": time_limit,
                }
            )
            test_id = test_obj.id
            self.current_edit_test_id = test_id
            if not self.btn_save_edit.winfo_ismapped():
                self.btn_save_edit.pack(side="left", padx=(0, 5))

        created_questions = 0
        for block in blocks:
            lines = [l.strip() for l in block.splitlines() if l.strip()]
            if not lines:
                continue

            q_text = lines[0]
            variants_lines = [l for l in lines[1:] if l.startswith("<variant>")]
            if not variants_lines:
                continue

            q_obj = self.questions_repo.create(
                {
                    "test_id": test_id,
                    "q_text": q_text,
                }
            )

            correct_done = False
            for v in variants_lines:
                a_text = v[len("<variant>") :].strip()
                if not a_text:
                    continue
                is_correct = not correct_done
                correct_done = True
                self.answers_repo.create(
                    {
                        "question_id": q_obj.id,
                        "a_text": a_text,
                        "is_correct": int(is_correct),
                    }
                )

            if correct_done:
                created_questions += 1

        messagebox.showinfo(
            "Готово",
            f"Тест '{name_from_form}' загружен/обновлён.\nВопросов создано: {created_questions}",
        )
        self.load_manager_tests()
