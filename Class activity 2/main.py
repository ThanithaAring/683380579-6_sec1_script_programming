# my-oop-task-manager/main.py
import sys

from src.task_manager import TaskManager

STUDENT_NAME = "นางสาวธนิษฐา อภิรัตน์มนตรี"
STUDENT_ID = "683380579-6"


def display_menu():
    print("\n--- OOP Task Manager Menu ---")
    print("1. Add Task")
    print("2. List Tasks")
    print("3. Complete Task")
    print("4. Delete Task")
    print("5. Exit")
    print("-----------------------------")


def ask_task_id(prompt):
    """Returns the ID as an int, or None if the user typed something that isn't a number."""
    text = input(prompt).strip()
    try:
        return int(text)
    except ValueError:
        print("Invalid input. Please enter a number for Task ID.")
        return None


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    print("=" * 40)
    print("  OOP Task Manager (Week 8)")
    print(f"  {STUDENT_NAME} | {STUDENT_ID}")
    print("=" * 40)

    manager = TaskManager()          # create one TaskManager object

    while True:
        display_menu()
        try:
            choice = input("Enter your choice (1-5): ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nExiting Task Manager. Goodbye!")
            break

        if choice == "1":
            manager.add_task(input("Enter task description: "))
        elif choice == "2":
            manager.list_tasks()
        elif choice == "3":
            task_id = ask_task_id("Enter ID of task to complete: ")
            if task_id is not None:
                manager.complete_task(task_id)
        elif choice == "4":
            task_id = ask_task_id("Enter ID of task to delete: ")
            if task_id is not None:
                manager.delete_task(task_id)
        elif choice == "5":
            print("Exiting Task Manager. Goodbye!")
            break
        else:
            print("Invalid choice. Please enter a number between 1 and 5.")


if __name__ == "__main__":
    main()
