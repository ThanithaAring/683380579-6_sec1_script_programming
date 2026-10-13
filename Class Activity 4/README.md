# Enhanced Task Manager (Week 11: Project Planning & Design)

**ผู้จัดทำ:** นางสาวธนิษฐา อภิรัตน์มนตรี  
**รหัสนักศึกษา:** 683380579-6

A command-line Task Manager redesigned into separate layers (models, data, logic, interface). The full design – requirements, architecture, data model, pseudocode and decisions – is in **[PLAN.md](PLAN.md)**.

Compared with the starter skeleton, the planned features **search, filter and sort are fully implemented** (they were TODO placeholders).

## Features
* Three task types: normal, due date, priority – all with **tags**
* List, complete, delete (with confirmation)
* **Search** – keyword in description or tags, case-insensitive
* **Filter** – status, due-date range, priority, tags; any combination
* **Sort** – id, description, completed, due_date, priority; ascending or descending
* Header shows total / completed / pending / overdue; overdue tasks are marked `(OVERDUE)`
* Auto-save to `data/tasks.json`; invalid input never crashes the program

## How to Run
```powershell
chcp 65001        # (Windows) so Thai text displays correctly
python main.py    # or: py main.py
```
No external packages needed.

### Tests
```powershell
python -m unittest discover tests -v
```

## Project Structure
```
enhanced-task-manager-design/
├── src/
│   ├── __init__.py
│   ├── task.py              # Task, DueDateTask, PriorityTask (+ tags)
│   ├── data_persistence.py  # JSON load/save
│   ├── task_manager.py      # business logic incl. search / filter / sort
│   └── cli_interface.py     # menus and input validation (Thai/English)
├── data/tasks.json          # sample tasks
├── tests/test_task_manager.py
├── screenshots/
├── main.py
├── PLAN.md                  # design document
└── README.md
```

## Screenshots

### Menu 4 – List All Tasks
![List all tasks](screenshots/option_4_list.png)

### Menu 7 – Search Tasks
![Search tasks](screenshots/option_7_search.png)

### Menu 9 – Sort Tasks
![Sort tasks](screenshots/option_9_sort.png)
