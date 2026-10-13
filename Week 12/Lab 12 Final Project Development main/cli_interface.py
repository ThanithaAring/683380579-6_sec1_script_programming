# final-task-manager-project/src/cli_interface.py
"""Command-line interface. Only handles input/output; all logic lives in TaskManager."""
import datetime

from .task import DATE_FORMAT, PRIORITIES
from .task_manager import SORT_CRITERIA

LINE = "=" * 44
THIN = "-" * 44


class CLIInterface:
    def __init__(self, task_manager, owner_name="", owner_id=""):
        self.manager = task_manager
        self.owner_name = owner_name
        self.owner_id = owner_id
        self.actions = {
            '1': self.add_normal_task,
            '2': self.add_due_date_task,
            '3': self.add_priority_task,
            '4': self.list_tasks,
            '5': self.complete_task,
            '6': self.delete_task,
            '7': self.search_tasks,
            '8': self.filter_tasks,
            '9': self.sort_tasks,
            '10': self.manage_tags,
        }

    # ---------- display ----------
    def show_banner(self):
        print(LINE)
        print("   ENHANCED TASK MANAGER  (Week 12 Final Project)")
        if self.owner_name:
            print(f"   {self.owner_name}  |  {self.owner_id}")
        print(LINE)

    def display_menu(self):
        s = self.manager.summary()
        print(f"\n{LINE}")
        print("--- Enhanced Task Manager Menu ---")
        print(f"Tasks: {s['total']} | Pending: {s['pending']} | Completed: {s['completed']} | Overdue: {s['overdue']}")
        print(LINE)
        print(" 1. Add Normal Task        6. Delete Task")
        print(" 2. Add Due Date Task      7. Search Tasks")
        print(" 3. Add Priority Task      8. Filter Tasks")
        print(" 4. List All Tasks         9. Sort Tasks")
        print(" 5. Complete Task         10. Add / Remove Tag")
        print(" 0. Exit")
        print(THIN)

    @staticmethod
    def display_tasks(tasks, title="Tasks"):
        print(f"\n--- {title} (Total: {len(tasks)}) ---")
        if not tasks:
            print("  (no tasks found)")
        for task in tasks:
            print(f"  * {task}")
        print(THIN)

    # ---------- input helpers ----------
    @staticmethod
    def ask(prompt):
        return input(prompt).strip()

    def ask_description(self):
        while True:
            text = self.ask("Enter task description: ")
            if text:
                return text
            print("[Error] Description cannot be empty.")

    def ask_date(self, prompt, allow_blank=False):
        while True:
            text = self.ask(prompt)
            if not text and allow_blank:
                return None
            try:
                return datetime.datetime.strptime(text, DATE_FORMAT).date()
            except ValueError:
                print("[Error] Use the format YYYY-MM-DD (e.g. 2026-12-31).")

    def ask_priority(self, allow_blank=False):
        while True:
            text = self.ask("Enter priority (High/Medium/Low"
                            + (", blank = any" if allow_blank else "") + "): ").capitalize()
            if not text and allow_blank:
                return None
            if text in PRIORITIES:
                return text
            print("[Error] Priority must be High, Medium or Low.")

    def ask_tags(self, prompt="Enter tags (comma-separated, e.g. study,project - optional): "):
        text = self.ask(prompt)
        return [t.strip().lower() for t in text.split(',') if t.strip()]

    def ask_task_id(self, prompt):
        text = self.ask(prompt)
        try:
            return int(text)
        except ValueError:
            print("[Error] Task ID must be a number.")
            return None

    def ask_yes_no(self, prompt, allow_blank=True):
        while True:
            text = self.ask(prompt).lower()
            if text in ('y', 'yes'):
                return True
            if text in ('n', 'no'):
                return False
            if not text and allow_blank:
                return None
            print("[Error] Please answer yes or no.")

    # ---------- menu actions ----------
    def add_normal_task(self):
        task = self.manager.add_normal_task(self.ask_description(), tags=self.ask_tags())
        print(f"[Success] Normal Task '{task.description}' added with ID {task.id}.")

    def add_due_date_task(self):
        description = self.ask_description()
        due = self.ask_date("Enter due date (YYYY-MM-DD): ")
        task = self.manager.add_due_date_task(description, due, tags=self.ask_tags())
        print(f"[Success] Due Date Task '{task.description}' (Due: {due}) added with ID {task.id}.")

    def add_priority_task(self):
        description = self.ask_description()
        priority = self.ask_priority()
        task = self.manager.add_priority_task(description, priority, tags=self.ask_tags())
        print(f"[Success] Priority Task '{task.description}' (Priority: {priority}) added with ID {task.id}.")

    def list_tasks(self):
        self.display_tasks(self.manager.get_all_tasks(), "Your Tasks")

    def complete_task(self):
        task_id = self.ask_task_id("Enter ID of task to complete: ")
        if task_id is not None:
            ok, msg = self.manager.complete_task(task_id)
            print(("[Success] " if ok else "[Info] ") + msg)

    def delete_task(self):
        task_id = self.ask_task_id("Enter ID of task to delete: ")
        if task_id is None:
            return
        task = self.manager.get_task_by_id(task_id)
        if task is None:
            print(f"[Info] Task ID {task_id} not found.")
            return
        if self.ask_yes_no(f"Delete '{task.description}'? (yes/no): ", allow_blank=False):
            ok, msg = self.manager.delete_task(task_id)
            print(("[Success] " if ok else "[Info] ") + msg)
        else:
            print("[Info] Delete cancelled.")

    def search_tasks(self):
        keyword = self.ask("Enter search keyword (description or tag): ")
        if not keyword:
            print("[Error] Keyword cannot be empty.")
            return
        self.display_tasks(self.manager.search_tasks(keyword), f"Search Results for '{keyword}'")

    def filter_tasks(self):
        print("\n--- Filter Tasks (leave blank to skip a filter) ---")
        status = self.ask_yes_no("Completed? (yes/no): ")
        before = self.ask_date("Due on or before (YYYY-MM-DD): ", allow_blank=True)
        after = self.ask_date("Due on or after (YYYY-MM-DD): ", allow_blank=True)
        priority = self.ask_priority(allow_blank=True)
        tags = self.ask_tags("Must have ALL these tags (comma-separated): ")
        results = self.manager.filter_tasks(status=status, due_date_before=before, due_date_after=after,
                                            priority_level=priority, contains_tags=tags or None)
        self.display_tasks(results, "Filtered Tasks")

    def sort_tasks(self):
        print("\n--- Sort Tasks ---")
        print(f"Criteria: {', '.join(SORT_CRITERIA)}")
        criterion = self.ask("Sort by (default: id): ").lower() or "id"
        if criterion not in SORT_CRITERIA:
            print(f"[Error] Unknown criterion '{criterion}'.")
            return
        reverse = bool(self.ask_yes_no("Descending order? (yes/no, default: no): "))
        tasks = self.manager.sort_tasks(criterion, reverse)
        self.display_tasks(tasks, f"Sorted by {criterion} ({'Descending' if reverse else 'Ascending'})")

    def manage_tags(self):
        task_id = self.ask_task_id("Enter task ID: ")
        if task_id is None:
            return
        action = self.ask("Type 'add' or 'remove': ").lower()
        if action not in ('add', 'remove'):
            print("[Error] Please type 'add' or 'remove'.")
            return
        tag = self.ask("Tag: ")
        if action == 'add':
            ok, msg = self.manager.add_tag_to_task(task_id, tag)
        else:
            ok, msg = self.manager.remove_tag_from_task(task_id, tag)
        print(("[Success] " if ok else "[Info] ") + msg)

    # ---------- main loop ----------
    def run(self):
        self.show_banner()
        while True:
            self.display_menu()
            try:
                choice = self.ask("Enter your choice (0-10): ")
                if choice == '0':
                    print("Exiting Task Manager. Goodbye!")
                    break
                action = self.actions.get(choice)
                if action:
                    action()
                else:
                    print("[Error] Invalid choice. Please enter a number from 0 to 10.")
            except (KeyboardInterrupt, EOFError):
                print("\nExiting Task Manager. Goodbye!")
                break
