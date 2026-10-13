# Project Plan: Enhanced Task Manager CLI (Final Version)

**ผู้จัดทำ:** นางสาวธนิษฐา อภิรัตน์มนตรี (683380579-6)

## 1. Goal
Build a reliable command-line task manager that applies OOP, modular design, JSON persistence, `datetime`, error handling and testing.

## 2. Requirements and Status

| Requirement | Status |
|---|---|
| Add / list / complete / delete tasks | Done |
| Task types: Normal, DueDate, Priority | Done |
| Tags on every task, add/remove tags | Done |
| Search (description + tags, partial, case-insensitive) | Done |
| Filter (status, due before/after, priority, tags – combined) | Done |
| Sort (id, description, completed, due_date, priority, asc/desc) | Done |
| Save to / load from `data/tasks.json` | Done |
| Input validation – the program never crashes on bad input | Done |
| Unit tests | Done (19 tests) |

## 3. Architecture

```
main.py ──► CLIInterface ──► TaskManager ──► DataPersistence ──► data/tasks.json
                                  │
                                  └── Task / DueDateTask / PriorityTask
```

| Module | Responsibility |
|---|---|
| `task.py` | Data models. Subclasses add their own fields through `_extra_details()` so `__str__` is written once. |
| `data_persistence.py` | JSON I/O. Uses `_type` to rebuild the correct class, `setdefault('tags', [])` for old files, and writes through a temp file so a crash can't corrupt data. |
| `task_manager.py` | All business logic. Never prints or reads input. |
| `cli_interface.py` | All input/output. Uses a dictionary to map menu numbers to methods. |
| `main.py` | Wires everything together. |

## 4. Implementation Notes & Challenges

**Tags** – Tags are normalized (trimmed, lowercased) in one place (`normalize_tag`) so search, filter and duplicates all behave the same.

**Filtering** – Each filter narrows the list in turn (AND logic). Date and priority filters use `isinstance()` so only tasks that actually have that field can match. Tag filtering uses `set.issubset()` – the task must have *all* requested tags.

**Sorting with missing fields** – The starter code gave tasks without a due date `date.max` as their key, so with `reverse=True` they jumped to the *top*. I sort the tasks that have the field separately and always append the others at the end, so reversing only reverses the meaningful part. Priority uses a map `High=1, Medium=2, Low=3`. The task ID is a secondary key for stable ordering.

**Input validation** – Dates must be `YYYY-MM-DD`, priority must be High/Medium/Low, IDs must be numbers; the CLI asks again or shows an error instead of crashing. Ctrl+C exits cleanly.

**Thai text** – JSON is saved with `ensure_ascii=False` and stdout is set to UTF-8 so Thai descriptions display correctly in the Windows terminal.

## 5. Testing
`python -m unittest discover tests` – each test uses its own temporary JSON file, so tests never touch the real `data/tasks.json`.

## 6. Lessons Learned
* Keeping logic out of the CLI made the features easy to test without typing into menus.
* Edge cases (empty keywords, missing tags in old files, reverse sorting) only showed up once I wrote tests for them.

## 7. Future Work
GUI, SQLite storage, due-date reminders, recurring tasks, CSV export.
