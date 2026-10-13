# enhanced-task-manager-design/src/data_persistence.py
"""Loads and saves tasks as JSON."""
import json
import os

from .task import Task, DueDateTask, PriorityTask

TASK_TYPES = {"Task": Task, "DueDateTask": DueDateTask, "PriorityTask": PriorityTask}
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class DataPersistence:
    """Reads tasks from and writes tasks to a JSON file."""

    def __init__(self, data_file='data/tasks.json'):
        # Relative paths are resolved from the project root, so the app works
        # no matter which folder it is launched from.
        self.path = data_file if os.path.isabs(data_file) else os.path.join(PROJECT_ROOT, data_file)

    def load_tasks(self):
        """Returns a list of Task objects. Bad or missing files give an empty list."""
        if not os.path.exists(self.path):
            return []
        try:
            with open(self.path, 'r', encoding='utf-8') as f:
                raw_tasks = json.load(f)
        except json.JSONDecodeError:
            print("Warning: tasks.json is empty or corrupted. Starting with an empty task list.")
            return []
        except OSError as e:
            print(f"Warning: could not read tasks file ({e}). Starting with an empty task list.")
            return []

        tasks = []
        for item in raw_tasks:
            data = dict(item)
            task_type = data.pop('_type', 'Task')
            data.setdefault('tags', [])          # older files may have no tags
            cls = TASK_TYPES.get(task_type)
            if cls is None:
                print(f"Warning: unknown task type '{task_type}' (ID {data.get('id', '?')}) skipped.")
                continue
            try:
                tasks.append(cls(**data))
            except (TypeError, ValueError) as e:
                print(f"Warning: invalid task data (ID {data.get('id', '?')}) skipped: {e}")
        return tasks

    def save_tasks(self, tasks):
        """Writes all tasks to disk (via a temp file so a crash can't corrupt the data)."""
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        temp_path = self.path + '.tmp'
        with open(temp_path, 'w', encoding='utf-8') as f:
            json.dump([t.to_dict() for t in tasks], f, indent=4, ensure_ascii=False)
        os.replace(temp_path, self.path)
