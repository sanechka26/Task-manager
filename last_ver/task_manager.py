import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry

class TaskManagerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Task Manager (Оценка 4)")

        # Список задач
        self.tasks = []

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
        # giga chat
        self.generate_btn = ttk.Button(root, text="Сгенерировать", command=self.start_generation)
        self.generate_btn.grid(row=1, column=2, padx=5)
        self.progress = ttk.Progressbar(root, mode='indeterminate')
        self.progress.grid(row=1, column=3, padx=5)
    #giga chat
    def start_generation(self):
        title = self.task_entry.get().strip()
        if not title:
            messagebox.showwarning("Ошибка", "Введите заголовок задачи")
            return

        self.progress.start()
        threading.Thread(target=self.generate_description).start()

    def generate_description(self):
        try:
            description = generate_task_description(self.task_entry.get())
            self.desc_entry.delete(0, tk.END)
            self.desc_entry.insert(0, description)
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))
        finally:
            self.progress.stop()

    def add_task(self):
        title = self.task_entry.get()
        description = self.desc_entry.get()
        priority = self.priority_var.get()
        date = self.date_entry.get_date()
        if title and description:
            task = {
                "title": title,
                "description": description,
                "priority": priority,
                "date": date,
                "status": "Текущая"
            }
            self.tasks.append(task)
            self.update_task_listbox()
            self.task_entry.delete(0, tk.END)
            self.desc_entry.delete(0, tk.END)
        else:
            messagebox.showwarning("Ошибка", "Заполните все поля!")

    def update_task_listbox(self):
        self.task_listbox.delete(0, tk.END)
        for task in self.tasks:
            status = "[Выполнено] " if task["status"] == "Выполнена" else ""
            task_text = f"{status}{task['title']} - {task['description']} (Приоритет: {task['priority']}, Дата: {task['date']})"
            self.task_listbox.insert(tk.END, task_text)

    def mark_completed(self):
        try:
            selected_index = self.task_listbox.curselection()[0]
            self.tasks[selected_index]["status"] = "Выполнена"
            self.update_task_listbox()
        except IndexError:
            messagebox.showwarning("Ошибка", "Выберите задачу!")

    def apply_filter(self, event):
        filter_type = self.filter_var.get()
        filtered_tasks = []
        for task in self.tasks:
            if filter_type == "Все":
                filtered_tasks.append(task)
            elif filter_type == "Текущие" and task["status"] == "Текущая":
                filtered_tasks.append(task)
            elif filter_type == "Выполненные" and task["status"] == "Выполнена":
                filtered_tasks.append(task)
        self.task_listbox.delete(0, tk.END)
        for task in filtered_tasks:
            status = "[Выполнено] " if task["status"] == "Выполнена" else ""
            task_text = f"{status}{task['title']} - {task['description']} (Приоритет: {task['priority']}, Дата: {task['date']})"
            self.task_listbox.insert(tk.END, task_text)

    def edit_task(self):
        try:
            selected_index = self.task_listbox.curselection()[0]
            task = self.tasks[selected_index]
            # Открытие окна для редактирования
            edit_window = tk.Toplevel(self.root)
            edit_window.title("Редактирование задачи")

            tk.Label(edit_window, text="Заголовок:").grid(row=0, column=0, padx=10, pady=5)
            title_entry = tk.Entry(edit_window, width=50)
            title_entry.grid(row=0, column=1, padx=10, pady=5)
            title_entry.insert(0, task["title"])

            tk.Label(edit_window, text="Описание:").grid(row=1, column=0, padx=10, pady=5)
            desc_entry = tk.Entry(edit_window, width=50)
            desc_entry.grid(row=1, column=1, padx=10, pady=5)
            desc_entry.insert(0, task["description"])

            tk.Label(edit_window, text="Приоритет:").grid(row=2, column=0, padx=10, pady=5)
            priority_var = tk.StringVar(value=task["priority"])
            priority_menu = ttk.Combobox(edit_window, textvariable=priority_var, values=["Высокий", "Средний", "Низкий"])
            priority_menu.grid(row=2, column=1, padx=10, pady=5)

            tk.Label(edit_window, text="Дата выполнения:").grid(row=3, column=0, padx=10, pady=5)
            date_entry = DateEntry(edit_window, width=12, background='darkblue', foreground='white', borderwidth=2)
            date_entry.grid(row=3, column=1, padx=10, pady=5)
            date_entry.set_date(task["date"])

            def save_changes():
                task["title"] = title_entry.get()
                task["description"] = desc_entry.get()
                task["priority"] = priority_var.get()
                task["date"] = date_entry.get_date()
                self.update_task_listbox()
                edit_window.destroy()

            tk.Button(edit_window, text="Сохранить изменения", command=save_changes).grid(row=4, column=0, columnspan=2, pady=10)

        except IndexError:
            messagebox.showwarning("Ошибка", "Выберите задачу!")

    def delete_task(self):
        try:
            selected_index = self.task_listbox.curselection()[0]
            del self.tasks[selected_index]
            self.update_task_listbox()
        except IndexError:
            messagebox.showwarning("Ошибка", "Выберите задачу!")

if __name__ == "__main__":
    root = tk.Tk()
    app = TaskManagerApp(root)
    root.mainloop()
