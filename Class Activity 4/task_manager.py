# enhanced-task-manager-design/src/task_manager.py
"""Business logic: add, complete, delete, tag, search, filter and sort tasks."""
import datetime
import logging

from .data_persistence import DataPersistence
from .task import Task, DueDateTask, PriorityTask, normalize_tag

logger = logging.getLogger(__name__)

SORT_CRITERIA = ("id", "description", "completed", "due_date", "priority")


class TaskManager:
    """Holds the task list and saves every change through DataPersistence."""

    PRIORITY_MAP = {"High": 1, "Medium": 2, "Low": 3}

    def __init__(self, data_file='data/tasks.json'):
        self.persistence = DataPersistence(data_file)
        self.tasks = self.persistence.load_tasks()
        self.next_id = max((t.id for t in self.tasks), default=0) + 1

    def _save(self):
        self.persistence.save_tasks(self.tasks)
        logger.info("Tasks saved (%d total).", len(self.tasks))

    def _add(self, task):
        self.tasks.append(task)
        self.next_id += 1
        self._save()
        return task

    # ---------- create ----------
    def add_normal_task(self, description, tags=None):
        return self._add(Task(self.next_id, description, tags=tags))

    def add_due_date_task(self, description, due_date, tags=None):
        """Returns the new task, or None if the date is invalid."""
        try:
            return self._add(DueDateTask(self.next_id, description, due_date, tags=tags))
        except (ValueError, TypeError):
            return None

    def add_priority_task(self, description, priority, tags=None):
        """Returns the new task, or None if the priority is invalid."""
        try:
            return self._add(PriorityTask(self.next_id, description, priority, tags=tags))
        except ValueError:
            return None

    # ---------- read / update / delete ----------
    def get_all_tasks(self):
        return list(self.tasks)

    def get_task_by_id(self, task_id):
        return next((t for t in self.tasks if t.id == task_id), None)

    def complete_task(self, task_id):
        task = self.get_task_by_id(task_id)
        if task is None:
            return False, f"Task ID {task_id} not found."
        if task.completed:
            return False, f"Task ID {task_id} is already completed."
        task.mark_complete()
        self._save()
        return True, f"Task ID {task_id} marked as completed."

    def delete_task(self, task_id):
        task = self.get_task_by_id(task_id)
        if task is None:
            return False, f"Task ID {task_id} not found."
        self.tasks.remove(task)
        self._save()
        return True, f"Task ID {task_id} ('{task.description}') deleted."

    def add_tag_to_task(self, task_id, tag):
        task = self.get_task_by_id(task_id)
        if task is None:
            return False, f"Task ID {task_id} not found."
        if not normalize_tag(tag):
            return False, "Tag cannot be empty."
        if normalize_tag(tag) in task.tags:
            return False, f"Task ID {task_id} already has tag '{normalize_tag(tag)}'."
        task.add_tag(tag)
        self._save()
        return True, f"Tag '{normalize_tag(tag)}' added to task ID {task_id}."

    def remove_tag_from_task(self, task_id, tag):
        task = self.get_task_by_id(task_id)
        if task is None:
            return False, f"Task ID {task_id} not found."
        if not task.remove_tag(tag):
            return False, f"Task ID {task_id} has no tag '{normalize_tag(tag)}'."
        self._save()
        return True, f"Tag '{normalize_tag(tag)}' removed from task ID {task_id}."

    # ---------- search / filter / sort ----------
    def search_tasks(self, keyword):
        """Case-insensitive partial match on description or any tag."""
        keyword = (keyword or "").strip().lower()
        if not keyword:
            return []
        return [t for t in self.tasks
                if keyword in t.description.lower() or any(keyword in tag for tag in t.tags)]

    def filter_tasks(self, status=None, due_date_before=None, due_date_after=None,
                     priority_level=None, contains_tags=None):
        """
        Applies every given criterion (AND logic).
          status          True = completed, False = pending
          due_date_before / due_date_after   datetime.date (inclusive, DueDateTask only)
          priority_level  "High" / "Medium" / "Low" (PriorityTask only)
          contains_tags   list of tags - the task must have ALL of them
        """
        result = list(self.tasks)
        if status is not None:
            result = [t for t in result if t.completed == status]
        if due_date_before:
            result = [t for t in result if isinstance(t, DueDateTask) and t.due_date <= due_date_before]
        if due_date_after:
            result = [t for t in result if isinstance(t, DueDateTask) and t.due_date >= due_date_after]
        if priority_level:
            level = priority_level.strip().capitalize()
            result = [t for t in result if isinstance(t, PriorityTask) and t.priority == level]
        if contains_tags:
            wanted = {normalize_tag(tag) for tag in contains_tags if normalize_tag(tag)}
            result = [t for t in result if wanted.issubset(t.tags)]
        return result

    def sort_tasks(self, criterion="id", reverse=False):
        """
        Returns a sorted copy of the tasks.
        For 'due_date' and 'priority', tasks without that field always go LAST,
        even when reverse=True.
        """
        criterion = (criterion or "id").strip().lower()
        if criterion not in SORT_CRITERIA:
            raise ValueError(f"Unknown sort criterion '{criterion}'. Use one of: {', '.join(SORT_CRITERIA)}")

        tasks = list(self.tasks)
        if criterion == "id":
            return sorted(tasks, key=lambda t: t.id, reverse=reverse)
        if criterion == "description":
            return sorted(tasks, key=lambda t: (t.description.lower(), t.id), reverse=reverse)
        if criterion == "completed":
            return sorted(tasks, key=lambda t: (t.completed, t.id), reverse=reverse)

        if criterion == "due_date":
            has_field = [t for t in tasks if isinstance(t, DueDateTask)]
            key = lambda t: (t.due_date, t.id)
        else:  # priority
            has_field = [t for t in tasks if isinstance(t, PriorityTask)]
            key = lambda t: (self.PRIORITY_MAP[t.priority], t.id)
        others = sorted((t for t in tasks if t not in has_field), key=lambda t: t.id)
        return sorted(has_field, key=key, reverse=reverse) + others

    def summary(self):
        """Counts for the status bar shown in the CLI."""
        today = datetime.date.today()
        return {
            "total": len(self.tasks),
            "pending": sum(not t.completed for t in self.tasks),
            "completed": sum(t.completed for t in self.tasks),
            "overdue": sum(isinstance(t, DueDateTask) and t.is_overdue(today) for t in self.tasks),
        }
