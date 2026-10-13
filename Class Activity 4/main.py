# enhanced-task-manager-design/main.py
"""Entry point for the Enhanced Task Manager CLI."""
import sys

from src.cli_interface import CLIInterface
from src.task_manager import TaskManager

OWNER_NAME = "นางสาวธนิษฐา อภิรัตน์มนตรี"
OWNER_ID = "683380579-6"


def main():
    # Make Thai text print correctly in the Windows terminal
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    manager = TaskManager()
    CLIInterface(manager, OWNER_NAME, OWNER_ID).run()


if __name__ == "__main__":
    main()
