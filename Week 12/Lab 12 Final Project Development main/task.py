# final-task-manager-project/src/task.py
"""Task models: Task, DueDateTask and PriorityTask (all support tags)."""
import datetime

DATE_FORMAT = '%Y-%m-%d'
PRIORITIES = ("High", "Medium", "Low")


def normalize_tag(tag):
    """Trims whitespace and lowercases a tag."""
    return str(tag).strip().lower()


class Task:
    """Base task with an id, description, completion status and a list of tags."""

    def __init__(self, id, description, completed=False, tags=None):
        self.id = id
        self.description = description
        self.completed = completed
        self.tags = []
        for tag in tags or []:
            self.add_tag(tag)

    def mark_complete(self):
        """Marks the task as completed."""
        self.completed = True

    def add_tag(self, tag):
        """Adds a normalized tag, ignoring empty values and duplicates."""
        tag = normalize_tag(tag)
        if tag and tag not in self.tags:
            self.tags.append(tag)

    def remove_tag(self, tag):
        """Removes a tag if present. Returns True if something was removed."""
        tag = normalize_tag(tag)
        if tag in self.tags:
            self.tags.remove(tag)
            return True
        return False

    def to_dict(self):
        """Serializes the task for JSON, including a '_type' marker."""
        return {
            "id": self.id,
            "description": self.description,
            "completed": self.completed,
            "tags": list(self.tags),
            "_type": "Task",
        }

    def _extra_details(self):
        """Extra fields shown by subclasses (e.g. due date, priority)."""
        return []

    def __str__(self):
        status = "Completed" if self.completed else "Pending"
        parts = [f"ID: {self.id}", f"Description: {self.description}", f"Status: {status}"]
        parts += self._extra_details()
        if self.tags:
            parts.append(f"Tags: {', '.join(self.tags)}")
        return " | ".join(parts)

    def __repr__(self):
        return (f"{type(self).__name__}(id={self.id}, description={self.description!r}, "
                f"completed={self.completed}, tags={self.tags})")


class DueDateTask(Task):
    """A task with a due date (datetime.date)."""

    def __init__(self, id, description, due_date, completed=False, tags=None):
        super().__init__(id, description, completed, tags)
        if isinstance(due_date, str):
            self.due_date = datetime.datetime.strptime(due_date.strip(), DATE_FORMAT).date()
        elif isinstance(due_date, datetime.date):
            self.due_date = due_date
        else:
            raise TypeError("due_date must be a 'YYYY-MM-DD' string or a datetime.date")

    def is_overdue(self, today=None):
        """True if the task is pending and its due date has passed."""
        today = today or datetime.date.today()
        return not self.completed and self.due_date < today

    def to_dict(self):
        data = super().to_dict()
        data["due_date"] = self.due_date.strftime(DATE_FORMAT)
        data["_type"] = "DueDateTask"
        return data

    def _extra_details(self):
        text = f"Due: {self.due_date.strftime(DATE_FORMAT)}"
        if self.is_overdue():
            text += " (OVERDUE)"
        return [text]


class PriorityTask(Task):
    """A task with a priority level: High, Medium or Low."""

    def __init__(self, id, description, priority, completed=False, tags=None):
        super().__init__(id, description, completed, tags)
        priority = str(priority).strip().capitalize()
        if priority not in PRIORITIES:
            raise ValueError(f"Priority must be one of {list(PRIORITIES)}")
        self.priority = priority

    def to_dict(self):
        data = super().to_dict()
        data["priority"] = self.priority
        data["_type"] = "PriorityTask"
        return data

    def _extra_details(self):
        return [f"Priority: {self.priority}"]
