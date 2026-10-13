# my-oop-task-manager/src/task.py


class Task:
    """
    Represents one task.

    Attributes:
        id (int): unique number of the task
        description (str): what needs to be done
        completed (bool): True when the task is finished
    """

    def __init__(self, id, description, completed=False):
        """Constructor - runs automatically when a Task object is created."""
        self.id = id
        self.description = description
        self.completed = completed

    def mark_complete(self):
        """Changes this task's state to completed."""
        self.completed = True

    def to_dict(self):
        """Turns the object into a dict so it can be saved as JSON."""
        return {
            "id": self.id,
            "description": self.description,
            "completed": self.completed,
        }

    @classmethod
    def from_dict(cls, data):
        """Builds a Task object back from a dict loaded from JSON."""
        return cls(data["id"], data["description"], data.get("completed", False))

    def __str__(self):
        """Friendly text used by print(task)."""
        status = "COMPLETED" if self.completed else "PENDING"
        return f"ID: {self.id} | Description: {self.description} | Status: {status}"

    def __repr__(self):
        """Exact text for debugging, e.g. in the VS Code Variables pane."""
        return f"Task(id={self.id}, description={self.description!r}, completed={self.completed})"
