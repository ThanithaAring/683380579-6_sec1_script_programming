# my-oop-task-manager/src/task_manager.py
import json
import os

from .task import Task

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class TaskManager:
    """
    Manages a list of Task objects and saves them to a JSON file.

    Attributes:
        tasks (list[Task]): all tasks
        next_id (int): ID that the next new task will get
    """

    def __init__(self, data_file="data/tasks.json"):
        self.data_file = os.path.join(PROJECT_ROOT, data_file)
        self.tasks = self._load_tasks()
        self.next_id = self._get_next_task_id()

    # ---------- private helpers (start with _) ----------
    def _get_next_task_id(self):
        return max((task.id for task in self.tasks), default=0) + 1

    def _load_tasks(self):
        """Reads the JSON file and turns each dict into a Task object."""
        if not os.path.exists(self.data_file):
            return []
        try:
            with open(self.data_file, "r", encoding="utf-8") as f:
                return [Task.from_dict(item) for item in json.load(f)]
        except (json.JSONDecodeError, KeyError, TypeError):
            print("Warning: tasks.json is empty or corrupted. Starting with an empty task list.")
            return []

    def _save_tasks(self):
        """Turns every Task object into a dict and writes them to the JSON file."""
        os.makedirs(os.path.dirname(self.data_file), exist_ok=True)
        with open(self.data_file, "w", encoding="utf-8") as f:
            json.dump([task.to_dict() for task in self.tasks], f, indent=4, ensure_ascii=False)

    def _find_task(self, task_id):
        for task in self.tasks:
            if task.id == task_id:
                return task
        return None

    # ---------- public methods ----------
    def add_task(self, description):
        """Creates a new Task object, stores it and saves."""
        description = description.strip()
        if not description:
            print("Error: Task description cannot be empty.")
            return None
        new_task = Task(self.next_id, description)
        self.tasks.append(new_task)
        self.next_id += 1
        self._save_tasks()
        print(f"Task '{description}' added with ID {new_task.id}.")
        return new_task

    def list_tasks(self):
        """Prints every task (print() calls Task.__str__ automatically)."""
        if not self.tasks:
            print("No tasks found.")
            return
        done = sum(1 for task in self.tasks if task.completed)
        print("\n--- Your Tasks ---")
        for task in self.tasks:
            print(task)
        print("------------------")
        print(f"Total: {len(self.tasks)} | Completed: {done} | Pending: {len(self.tasks) - done}")

    def complete_task(self, task_id):
        """Finds the task and calls its mark_complete() method."""
        task = self._find_task(task_id)
        if task is None:
            print(f"Error: Task with ID {task_id} not found.")
            return False
        if task.completed:
            print(f"Task ID {task_id} is already completed.")
            return False
        task.mark_complete()
        self._save_tasks()
        print(f"Task ID {task_id} marked as completed.")
        return True

    def delete_task(self, task_id):
        """Removes the task with this ID."""
        task = self._find_task(task_id)
        if task is None:
            print(f"Error: Task with ID {task_id} not found.")
            return False
        self.tasks.remove(task)
        self._save_tasks()
        print(f"Task ID {task_id} deleted successfully.")
        return True
