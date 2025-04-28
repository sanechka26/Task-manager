import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
import sqlite3
from datetime import datetime


class TaskDatabase:
    def __init__(self, db_name='tasker.db'):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self.create_tables()

    def create_tables(self):
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            priority TEXT CHECK(priority IN ('Высокий', 'Средний', 'Низкий')),
            due_date DATE,
            status TEXT CHECK(status IN ('Текущая', 'Выполнена')),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        self.conn.commit()

    def add_task(self, title, description, priority, due_date, status='Текущая'):
        self.cursor.execute('''
        INSERT INTO tasks (title, description, priority, due_date, status)
        VALUES (?, ?, ?, ?, ?)
        ''', (title, description, priority, due_date, status))
        self.conn.commit()
        return self.cursor.lastrowid

    def get_all_tasks(self, filter_type='Все'):
        query = 'SELECT * FROM tasks'
        if filter_type == 'Текущие':
            query += " WHERE status = 'Текущая'"
        elif filter_type == 'Выполненные':
            query += " WHERE status = 'Выполнена'"
        query += " ORDER BY CASE priority WHEN 'Высокий' THEN 1 WHEN 'Средний' THEN 2 ELSE 3 END, due_date"
        self.cursor.execute(query)
        return self.cursor.fetchall()

    def update_task(self, task_id, title=None, description=None, priority=None, due_date=None, status=None):
        updates = []
        params = []

        if title:
            updates.append("title = ?")
            params.append(title)
        if description:
            updates.append("description = ?")
            params.append(description)
        if priority:
            updates.append("priority = ?")
            params.append(priority)
        if due_date:
            updates.append("due_date = ?")
            params.append(due_date)
        if status:
            updates.append("status = ?")
            params.append(status)

        if updates:
            query = "UPDATE tasks SET " + ", ".join(updates) + " WHERE id = ?"
            params.append(task_id)
            self.cursor.execute(query, params)
            self.conn.commit()

    def delete_task(self, task_id):
        self.cursor.execute('DELETE FROM tasks WHERE id = ?', (task_id,))
        self.conn.commit()
        return self.cursor.rowcount > 0

    def close(self):
        self.conn.close()


class TaskManagerApp:
    def __init__(self, root):
        self.db = TaskDatabase()
        self.root = root
        self.root.title("Task Manager (Оценка 4)")

        # Интерфейс
        self.task_label = tk.Label(root, text="Заголовок задачи:")
        self.task_label.grid(row=0, column=0, padx=10, pady=5)
        self.task_entry = tk.Entry(root, width=50)
        self.task_entry.grid(row=0, column=1, padx=10, pady=5)

        self.desc_label = tk.Label(root, text="Описание задачи:")
        self.desc_label.grid(row=1, column=0, padx=10, pady=5)
        self.desc_entry = tk.Entry(root, width=50)
        self.desc_entry.grid(row=1, column=1, padx=10, pady=5)

        # Календарь
        self.date_label = tk.Label(root, text="Дата выполнения:")
        self.date_label.grid(row=2, column=0, padx=10, pady=5)
        self.date_entry = DateEntry(root, width=12, background='darkblue', foreground='white', borderwidth=2)
        self.date_entry.grid(row=2, column=1, padx=10, pady=5)

        # Приоритет
        self.priority_label = tk.Label(root, text="Приоритет:")
        self.priority_label.grid(row=3, column=0, padx=10, pady=5)
        self.priority_var = tk.StringVar(value="Средний")
        self.priority_menu = ttk.Combobox(root, textvariable=self.priority_var, values=["Высокий", "Средний", "Низкий"])
        self.priority_menu.grid(row=3, column=1, padx=10, pady=5)

        # Добавление задачи
        self.add_button = tk.Button(root, text="Добавить задачу", command=self.add_task)
        self.add_button.grid(row=4, column=0, columnspan=2, pady=10)

        # Прокручиваемый список задач
        self.task_listbox = tk.Listbox(root, width=70, height=10)
        self.task_listbox.grid(row=5, column=0, columnspan=2, padx=10, pady=5)

        # Управление статусом задач
        self.complete_button = tk.Button(root, text="Отметить как выполнено", command=self.mark_completed)
        self.complete_button.grid(row=6, column=0, columnspan=2, pady=5)

        # Фильтрация задач
        self.filter_label = tk.Label(root, text="Фильтр:")
        self.filter_label.grid(row=7, column=0, padx=10, pady=5)
        self.filter_var = tk.StringVar(value="Все")
        self.filter_menu = ttk.Combobox(root, textvariable=self.filter_var, values=["Все", "Текущие", "Выполненные"])
        self.filter_menu.grid(row=7, column=1, padx=10, pady=5)
        self.filter_menu.bind("<<ComboboxSelected>>", self.apply_filter)

        # Редактирование задач
        self.edit_button = tk.Button(root, text="Редактировать задачу", command=self.edit_task)
        self.edit_button.grid(row=8, column=0, columnspan=2, pady=5)

        # Удаление задач
        self.delete_button = tk.Button(root, text="Удалить задачу", command=self.delete_task)
        self.delete_button.grid(row=9, column=0, columnspan=2, pady=5)

        # Первоначальное обновление списка задач
        self.update_task_listbox()

    def add_task(self):
        title = self.task_entry.get()
        description = self.desc_entry.get()
        priority = self.priority_var.get()
        date = self.date_entry.get_date()

        if title and description:
            self.db.add_task(title, description, priority, date)
            self.update_task_listbox()
            self.task_entry.delete(0, tk.END)
            self.desc_entry.delete(0, tk.END)
        else:
            messagebox.showwarning("Ошибка", "Заполните все поля!")

    def update_task_listbox(self):
        self.task_listbox.delete(0, tk.END)
        filter_type = self.filter_var.get()
        tasks = self.db.get_all_tasks(filter_type)

        for task in tasks:
            task_id, title, description, priority, due_date, status, created_at = task
            status = "[Выполнено] " if status == "Выполнена" else ""
            task_text = f"{status}{title} - {description} (Приоритет: {priority}, Дата: {due_date})"
            self.task_listbox.insert(tk.END, task_text)

    def mark_completed(self):
        try:
            selected_index = self.task_listbox.curselection()[0]
            tasks = self.db.get_all_tasks(self.filter_var.get())
            task_id = tasks[selected_index][0]
            self.db.update_task(task_id, status="Выполнена")
            self.update_task_listbox()
        except IndexError:
            messagebox.showwarning("Ошибка", "Выберите задачу!")

    def apply_filter(self, event=None):
        self.update_task_listbox()

    def edit_task(self):
        try:
            selected_index = self.task_listbox.curselection()[0]
            tasks = self.db.get_all_tasks(self.filter_var.get())
            task = tasks[selected_index]
            task_id, title, description, priority, due_date, status, created_at = task

            edit_window = tk.Toplevel(self.root)
            edit_window.title("Редактирование задачи")

            tk.Label(edit_window, text="Заголовок:").grid(row=0, column=0, padx=10, pady=5)
            title_entry = tk.Entry(edit_window, width=50)
            title_entry.grid(row=0, column=1, padx=10, pady=5)
            title_entry.insert(0, title)

            tk.Label(edit_window, text="Описание:").grid(row=1, column=0, padx=10, pady=5)
            desc_entry = tk.Entry(edit_window, width=50)
            desc_entry.grid(row=1, column=1, padx=10, pady=5)
            desc_entry.insert(0, description)

            tk.Label(edit_window, text="Приоритет:").grid(row=2, column=0, padx=10, pady=5)
            priority_var = tk.StringVar(value=priority)
            priority_menu = ttk.Combobox(edit_window, textvariable=priority_var, values=["Высокий", "Средний", "Низкий"])
            priority_menu.grid(row=2, column=1, padx=10, pady=5)

            tk.Label(edit_window, text="Дата выполнения:").grid(row=3, column=0, padx=10, pady=5)
            date_entry = DateEntry(edit_window, width=12, background='darkblue', foreground='white', borderwidth=2)
            date_entry.grid(row=3, column=1, padx=10, pady=5)
            date_entry.set_date(datetime.strptime(due_date, "%Y-%m-%d").date())

            def save_changes():
                self.db.update_task(
                    task_id,
                    title=title_entry.get(),
                    description=desc_entry.get(),
                    priority=priority_var.get(),
                    due_date=date_entry.get_date()
                )
                self.update_task_listbox()
                edit_window.destroy()

            tk.Button(edit_window, text="Сохранить изменения", command=save_changes).grid(row=4, column=0, columnspan=2, pady=10)

        except IndexError:
            messagebox.showwarning("Ошибка", "Выберите задачу!")

    def delete_task(self):
        try:
            selected_index = self.task_listbox.curselection()[0]
            tasks = self.db.get_all_tasks(self.filter_var.get())
            task_id = tasks[selected_index][0]
            if messagebox.askyesno("Подтверждение", "Вы уверены, что хотите удалить эту задачу?"):
                self.db.delete_task(task_id)
                self.update_task_listbox()
        except IndexError:
            messagebox.showwarning("Ошибка", "Выберите задачу!")


if __name__ == "__main__":
    root = tk.Tk()
    app = TaskManagerApp(root)
    root.protocol("WM_DELETE_WINDOW", lambda: [app.db.close(), root.destroy()])
    root.mainloop()