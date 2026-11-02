import threading
import tkinter as tk
from tkinter import ttk
from storage import load_data, save_tasks, set_settings
from wallpaper_engine import render_and_update_wallpaper

_current_manager_instance = None

class TaskManager(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("To-Do Desktop Manager")
        self.geometry("680x510")
        self.minsize(580, 360)
        self.configure(bg="#ffffff")
        self.attributes("-topmost", True)

        self.protocol("WM_DELETE_WINDOW", self.close_window)
        self.bind("<Escape>", lambda e: self.close_window())

        data = load_data()
        self.tasks = data.get("tasks", [])
        self.current_title = data.get("title", "Progetti")
        self.current_theme = data.get("theme", "auto")
        self.card_bg_var = tk.BooleanVar(value=data.get("card_bg", False))
        self.inline_entry = None

        self.style = ttk.Style(self)
        self.style.theme_use("clam")
        
        self.style.configure(
            "Treeview",
            background="#ffffff",
            foreground="#1e293b",
            fieldbackground="#ffffff",
            rowheight=30,
            font=("Arial", 10)
        )
        self.style.configure(
            "Treeview.Heading",
            background="#f8fafc",
            foreground="#334155",
            font=("Arial", 10, "bold"),
            relief="flat"
        )
        self.style.map("Treeview", background=[("selected", "#e2e8f0")], foreground=[("selected", "#0f172a")])

        self._build_ui()
        self._populate_tree()

    def _build_ui(self):
        top_bar = tk.Frame(self, bg="#f8fafc", bd=1, relief=tk.SOLID)
        top_bar.pack(fill=tk.X, padx=16, pady=(14, 4))

        tk.Label(
            top_bar, 
            text="Titolo:", 
            bg="#f8fafc", 
            fg="#475569", 
            font=("Segoe UI", 9, "bold")
        ).pack(side=tk.LEFT, padx=(10, 4), pady=8)

        self.ent_title = tk.Entry(
            top_bar, 
            font=("Arial", 10), 
            relief=tk.SOLID, 
            bd=1, 
            bg="#ffffff", 
            fg="#0f172a", 
            width=12
        )
        self.ent_title.pack(side=tk.LEFT, padx=4, pady=8)
        self.ent_title.insert(0, self.current_title)

        tk.Label(
            top_bar, 
            text="Tema:", 
            bg="#f8fafc", 
            fg="#475569", 
            font=("Segoe UI", 9, "bold")
        ).pack(side=tk.LEFT, padx=(10, 4), pady=8)

        self.combo_theme = ttk.Combobox(
            top_bar, 
            values=["Auto", "Tema Scuro", "Tema Chiaro"], 
            state="readonly", 
            width=12
        )
        theme_map = {"auto": 0, "dark": 1, "light": 2}
        self.combo_theme.current(theme_map.get(self.current_theme, 0))
        self.combo_theme.pack(side=tk.LEFT, padx=4, pady=8)

        chk_card = tk.Checkbutton(
            top_bar,
            text="Sfondo scheda",
            variable=self.card_bg_var,
            bg="#f8fafc",
            fg="#334155",
            activebackground="#f8fafc",
            font=("Segoe UI", 9, "bold")
        )
        chk_card.pack(side=tk.LEFT, padx=(10, 6), pady=8)

        self.btn_apply = tk.Button(
            top_bar,
            text="Salva ed Applica",
            bg="#2563eb",
            fg="#ffffff",
            activebackground="#1d4ed8",
            activeforeground="#ffffff",
            relief=tk.FLAT,
            padx=10,
            pady=3,
            font=("Segoe UI", 9, "bold"),
            command=self.save_and_apply
        )
        self.btn_apply.pack(side=tk.RIGHT, padx=10, pady=6)

        table_frame = tk.Frame(self, bg="#ffffff")
        table_frame.pack(fill=tk.BOTH, expand=True, padx=16, pady=(8, 8))

        columns = ("done", "text", "date")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", selectmode="extended")
        
        self.tree.heading("done", text="Stato")
        self.tree.heading("text", text="Task (doppio click per modificare)")
        self.tree.heading("date", text="Data/Info (max 16)")

        self.tree.column("done", width=65, anchor="center")
        self.tree.column("text", width=425, anchor="w")
        self.tree.column("date", width=125, anchor="center")

        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.tree.bind("<Double-1>", self.on_double_click)
        self.bind("<Delete>", lambda e: self.delete_selected())

        bottom_frame = tk.Frame(self, bg="#ffffff")
        bottom_frame.pack(fill=tk.X, padx=16, pady=(6, 14))

        btn_add = tk.Button(
            bottom_frame,
            text="+ Nuovo Task",
            bg="#10b981",
            fg="#ffffff",
            activebackground="#059669",
            activeforeground="#ffffff",
            relief=tk.FLAT,
            padx=12,
            pady=4,
            command=self.create_inline_task
        )
        btn_add.pack(side=tk.LEFT)

        tk.Label(
            bottom_frame, 
            text="Ctrl/Shift+Click selez. multipla • Canc elimina", 
            bg="#ffffff", 
            fg="#94a3b8", 
            font=("Segoe UI", 9)
        ).pack(side=tk.LEFT, padx=12)

        btn_del = tk.Button(
            bottom_frame, 
            text="Elimina selezionati", 
            bg="#ef4444", 
            fg="#ffffff", 
            activebackground="#dc2626", 
            activeforeground="#ffffff", 
            relief=tk.FLAT, 
            padx=10, 
            pady=4, 
            command=self.delete_selected
        )
        btn_del.pack(side=tk.RIGHT)

    def close_window(self):
        global _current_manager_instance
        _current_manager_instance = None
        if self.inline_entry:
            try:
                self.inline_entry.destroy()
            except Exception:
                pass
        self.destroy()
        self.quit()

    def save_and_apply(self):
        new_title = self.ent_title.get().rstrip(":").strip() or "Progetti"
        selected_index = self.combo_theme.current()
        theme_keys = ["auto", "dark", "light"]
        new_theme = theme_keys[selected_index] if 0 <= selected_index < len(theme_keys) else "auto"
        new_card_bg = bool(self.card_bg_var.get())

        self.current_title = new_title
        self.current_theme = new_theme
        set_settings(new_title, new_theme, new_card_bg)
        save_tasks(self.tasks)

        def worker():
            render_and_update_wallpaper(
                tasks=self.tasks,
                title=self.current_title,
                theme=self.current_theme,
                card_bg=new_card_bg
            )

        threading.Thread(target=worker, daemon=True).start()

    def _populate_tree(self):
        self.tree.delete(*self.tree.get_children())
        for task in self.tasks:
            status = "[x]" if task.get("completato", False) else "[ ]"
            date_val = str(task.get("data", ""))[:16]
            self.tree.insert("", tk.END, iid=str(task["id"]), values=(status, task.get("testo", ""), date_val))

    def create_inline_task(self):
        new_id = max([t.get("id", 0) for t in self.tasks], default=0) + 1
        new_task = {"id": new_id, "testo": "", "data": "", "completato": False}
        self.tasks.append(new_task)
        self._populate_tree()

        item_id = str(new_id)
        self.tree.selection_set(item_id)
        self.tree.see(item_id)
        self.start_inline_editing(item_id, column_id="#2")

    def on_double_click(self, event):
        if self.inline_entry:
            self.inline_entry.destroy()
            self.inline_entry = None

        item_id = self.tree.identify_row(event.y)
        column_id = self.tree.identify_column(event.x)
        if not item_id:
            return

        selected = self.tree.selection()
        if len(selected) > 1 and item_id in selected:
            return

        task_id = int(item_id)
        task = next((t for t in self.tasks if t["id"] == task_id), None)
        if not task:
            return

        if column_id == "#1":
            task["completato"] = not task.get("completato", False)
            self._populate_tree()
            self.save_and_apply()
            return

        if column_id in ("#2", "#3"):
            self.start_inline_editing(item_id, column_id)

    def start_inline_editing(self, item_id: str, column_id: str):
        if self.inline_entry:
            self.inline_entry.destroy()
            self.inline_entry = None

        task_id = int(item_id)
        task = next((t for t in self.tasks if t["id"] == task_id), None)
        if not task:
            return

        col_key = "testo" if column_id == "#2" else "data"
        bbox = self.tree.bbox(item_id, column=column_id)
        if not bbox:
            return

        x, y, w, h = bbox
        
        # Limite a 16 caratteri per il campo Data/Info
        if col_key == "data":
            vcmd = (self.register(lambda P: len(P) <= 16), "%P")
            self.inline_entry = tk.Entry(
                self.tree, 
                font=("Arial", 10), 
                relief=tk.SOLID, 
                bd=1, 
                bg="#ffffff", 
                fg="#0f172a",
                validate="key",
                validatecommand=vcmd
            )
        else:
            self.inline_entry = tk.Entry(
                self.tree, 
                font=("Arial", 10), 
                relief=tk.SOLID, 
                bd=1, 
                bg="#ffffff", 
                fg="#0f172a"
            )

        self.inline_entry.place(x=x, y=y, width=w, height=h)
        val_initial = str(task.get(col_key, ""))
        if col_key == "data":
            val_initial = val_initial[:16]
        self.inline_entry.insert(0, val_initial)
        self.inline_entry.focus_set()

        def save_inline(e=None):
            if not self.inline_entry:
                return
            new_value = self.inline_entry.get().strip()
            if col_key == "data":
                new_value = new_value[:16]

            self.inline_entry.destroy()
            self.inline_entry = None

            if not new_value and not task.get("testo") and not task.get("data"):
                self.tasks = [t for t in self.tasks if t["id"] != task_id]
            else:
                task[col_key] = new_value

            self._populate_tree()
            self.save_and_apply()

        def cancel_inline(e=None):
            if self.inline_entry:
                self.inline_entry.destroy()
                self.inline_entry = None
            if not task.get("testo") and not task.get("data"):
                self.tasks = [t for t in self.tasks if t["id"] != task_id]
                self._populate_tree()

        self.inline_entry.bind("<Return>", save_inline)
        self.inline_entry.bind("<FocusOut>", save_inline)
        self.inline_entry.bind("<Escape>", cancel_inline)

    def delete_selected(self):
        selected_ids = self.tree.selection()
        if not selected_ids:
            return
        ids_to_remove = {int(i) for i in selected_ids}
        self.tasks = [t for t in self.tasks if t["id"] not in ids_to_remove]
        self._populate_tree()
        self.save_and_apply()


def show_manager():
    global _current_manager_instance
    if _current_manager_instance is not None:
        try:
            _current_manager_instance.lift()
            _current_manager_instance.focus_force()
            return
        except Exception:
            _current_manager_instance = None

    _current_manager_instance = TaskManager()
    _current_manager_instance.mainloop()

if __name__ == "__main__":
    show_manager()