# Week 8: OOP Task Manager CLI

**ผู้จัดทำ:** นางสาวธนิษฐา อภิรัตน์มนตรี  
**รหัสนักศึกษา:** 683380579-6

The Task Manager CLI refactored from procedural code into **Object-Oriented Programming**: tasks are `Task` objects and all operations live in a `TaskManager` class.

## OOP Design

```
Task                                  TaskManager
├─ id, description, completed         ├─ tasks: list[Task]
├─ mark_complete()                    ├─ next_id
├─ to_dict()  / from_dict()           ├─ add_task(description)
├─ __str__()  -> for print()          ├─ list_tasks()
└─ __repr__() -> for debugging        ├─ complete_task(task_id) -> calls task.mark_complete()
                                      ├─ delete_task(task_id)
                                      └─ _load_tasks() / _save_tasks()   (JSON <-> Task objects)
```

* **Encapsulation** – a task's data and the method that changes it (`mark_complete`) are in the same class.
* **`self`** – every method uses `self` to reach the object's own attributes, e.g. `self.completed = True`.
* **JSON ↔ objects** – `to_dict()` before saving, `Task.from_dict()` after loading.
* `next_id` only counts up, so a deleted task's ID is never reused.

## How to Run
```powershell
python main.py        # or: py main.py
```
`data/tasks.json` already has one **COMPLETED** and one **PENDING** task, so menu **2** shows both right away.

### Tests
```powershell
python -m unittest discover tests -v
```

## Project Structure
```
my-oop-task-manager/
├── src/
│   ├── __init__.py
│   ├── task.py           # Task class
│   └── task_manager.py   # TaskManager class
├── data/tasks.json
├── tests/test_oop.py
├── screenshots/
├── main.py               # menu (CLI)
├── .gitignore
└── README.md
```

## Screenshot – Menu 2: List Tasks
![List tasks](screenshots/list_tasks.png)
