# Final Project: Enhanced Task Manager CLI

**ผู้จัดทำ:** นางสาวธนิษฐา อภิรัตน์มนตรี  
**รหัสนักศึกษา:** 683380579-6  
**รายวิชา:** Script Programming – Week 12 Final Project Development

A command-line task manager built with OOP and a modular design. Tasks are saved to JSON, can carry tags, and can be searched, filtered and sorted.

## Features

| Menu | Feature |
|---|---|
| 1–3 | Add a **Normal**, **Due Date** or **Priority** task, each with optional tags |
| 4 | List all tasks (overdue tasks are marked `(OVERDUE)`) |
| 5 | Complete a task by ID |
| 6 | Delete a task by ID (asks for confirmation) |
| 7 | **Search** – case-insensitive partial match on description and tags |
| 8 | **Filter** – any combination of status, due-date range, priority and tags (AND logic) |
| 9 | **Sort** – by id, description, completed, due_date or priority, ascending or descending |
| 10 | Add or remove a tag on an existing task |

The menu header shows live counts: total / pending / completed / overdue.

## How to Run

```powershell
py -m venv .venv
.venv\Scripts\activate          # macOS/Linux: source .venv/bin/activate
python main.py
```
No external packages are needed (standard library only).

### Run the tests
```powershell
python -m unittest discover tests -v
```
19 tests cover the task models, JSON save/load, CRUD, search, filter, sort and tags.

## Project Structure

```
final-task-manager-project/
├── src/
│   ├── __init__.py
│   ├── task.py              # Task, DueDateTask, PriorityTask (+ tags, overdue check)
│   ├── data_persistence.py  # JSON load/save, rebuilds the right class from "_type"
│   ├── task_manager.py      # Business logic: CRUD, tags, search, filter, sort, summary
│   └── cli_interface.py     # Menu, input validation, output
├── data/
│   └── tasks.json           # Pre-seeded demo tasks
├── tests/
│   └── test_task_manager.py
├── screenshots/
├── main.py
├── PLAN.md
├── .gitignore
└── README.md
```

## Screenshots

### Menu 4 – List All Tasks
![List all tasks](screenshots/option_list.png)

### Menu 7 – Search Tasks
![Search tasks](screenshots/option_search.png)

### Menu 9 – Sort Tasks by priority
![Sort tasks](screenshots/option_sort.png)

## Future Work
* GUI (Tkinter) or a small web interface (Flask)
* SQLite instead of JSON
* Reminders for tasks that are due soon
* Recurring tasks and export to CSV
