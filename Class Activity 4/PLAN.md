# Project Plan: Enhanced Task Manager CLI (Week 11)

**ผู้จัดทำ:** นางสาวธนิษฐา อภิรัตน์มนตรี  
**รหัสนักศึกษา:** 683380579-6

## 1. Introduction

The Task Manager from earlier weeks kept menus, logic and file handling together in a few files, which made new features hard to add. This plan redesigns it into separate layers and adds **tags, search, filter and sort**. The design was written first; the implementation followed it step by step (status in section 5).

**Problem it solves:** a student has tasks from many subjects with different deadlines and importance. The app should make it quick to see what is due, what is important, and what is already done.

## 2. Requirements

### 2.1 Functional Requirements

| ID | Requirement | Status |
|---|---|---|
| F1 | Add a normal task with description and optional tags | Done |
| F2 | Add a due-date task (`YYYY-MM-DD`) | Done |
| F3 | Add a priority task (High / Medium / Low) | Done |
| F4 | List all tasks with type-specific fields and tags | Done |
| F5 | Mark a task as completed | Done |
| F6 | Delete a task by ID (with confirmation) | Done |
| F7 | **Search** by keyword in description or tags (case-insensitive, partial) | Done |
| F8 | **Filter** by status, due-date range, priority, tags – any combination | Done |
| F9 | **Sort** by id, description, completed, due date, priority (asc/desc) | Done |
| F10 | Save to `data/tasks.json` after every change and load on start-up | Done |

### 2.2 Non-Functional Requirements

| ID | Requirement | How it is met |
|---|---|---|
| N1 | Usability | Thai/English menu, live counts in the header, clear success/error messages |
| N2 | Reliability | Invalid dates, priorities, IDs and menu choices are rejected without crashing; a corrupted JSON file starts an empty list |
| N3 | Data safety | Save writes to a temp file then replaces `tasks.json`, so a crash can't half-write it |
| N4 | Maintainability | One responsibility per module; docstrings; unit tests |
| N5 | Extensibility | New task types or storage back-ends can be added without touching the CLI |
| N6 | Performance | All operations are in-memory list work – instant for hundreds of tasks |

## 3. Design

### 3.1 Architecture (Separation of Concerns)

```
            ┌──────────────────────┐
  user ───► │   cli_interface.py   │  input / output only
            └──────────┬───────────┘
                       │ calls
            ┌──────────▼───────────┐
            │   task_manager.py    │  business logic: add, complete, delete,
            │                      │  search, filter, sort, summary
            └───────┬───────┬──────┘
         uses       │       │      saves / loads
   ┌────────────────▼─┐   ┌─▼──────────────────────┐
   │     task.py      │   │  data_persistence.py   │ ──► data/tasks.json
   │ Task             │   │  JSON <-> Task objects │
   │ ├ DueDateTask    │   └────────────────────────┘
   │ └ PriorityTask   │
   └──────────────────┘
main.py creates TaskManager + CLIInterface and starts the loop.
```

| Module | Responsibility | Must NOT do |
|---|---|---|
| `task.py` | Data models, tags, `to_dict()`, `__str__()` | read files, print menus |
| `data_persistence.py` | Read/write JSON, rebuild the right class from `_type` | know about menus or search |
| `task_manager.py` | All rules and operations on the task list | call `input()` or `print()` menus |
| `cli_interface.py` | Menus, prompts, validation, display | contain business rules |
| `main.py` | Wire the pieces together | anything else |

### 3.2 Data Model

```
Task
  id: int            description: str
  completed: bool    tags: list[str]   (trimmed, lower-case, no duplicates)
DueDateTask(Task)  + due_date: datetime.date      (+ is_overdue())
PriorityTask(Task) + priority: "High" | "Medium" | "Low"
```

JSON example (`_type` tells the loader which class to build):
```json
{"id": 2, "description": "Submit Week 11", "completed": false,
 "tags": ["assignment", "github"], "_type": "DueDateTask", "due_date": "2026-10-20"}
```
Older files without `tags` still load (`setdefault('tags', [])`).

### 3.3 Algorithm Design (pseudocode)

**search(keyword)**
```
k = lower(trim(keyword)); if k empty -> return []
return tasks where k in lower(description) OR any(k in tag for tag in tags)
```

**filter(status, before, after, priority, tags)** – each given filter narrows the list (AND):
```
result = all tasks
if status given   : keep completed == status
if before given   : keep DueDateTask with due_date <= before
if after given    : keep DueDateTask with due_date >= after
if priority given : keep PriorityTask with that priority
if tags given     : keep tasks whose tags contain ALL wanted tags (set.issubset)
```

**sort(criterion, reverse)**
```
id / description / completed -> sorted(..., key, reverse)
due_date / priority:
    with_field = tasks that have the field, sorted by (value, id), reverse applied
    others     = remaining tasks sorted by id
    return with_field + others      # tasks without the field are ALWAYS last
priority value map: High=1, Medium=2, Low=3
```
*Design decision:* the starter idea used `date.max` / `99` as the key for tasks without the field. With `reverse=True` that moves them to the **top**, which is confusing, so they are kept separate and appended last.

### 3.4 Interface Design (CLI)

```
1-3  add task (normal / due date / priority)     7  search
4    list all                                    8  filter (Enter skips a condition)
5    complete       6  delete (asks y/n)         9  sort (criterion + direction)
0    exit
```
Every prompt re-asks on invalid input instead of crashing.

## 4. Implementation Plan

1. Move models into `task.py`, add `tags` + `add_tag` / `remove_tag`.
2. Move JSON code into `data_persistence.py`; handle `_type` and missing `tags`.
3. Make `task_manager.py` use `DataPersistence` only (no file code).
4. Move all `input`/`print` into `cli_interface.py`; make `main.py` an orchestrator.
5. Implement search → filter → sort, testing each one before the next.
6. Write unit tests with a temporary JSON file so real data is never touched.

## 5. Status & Testing

All steps above are implemented. `python -m unittest discover tests -v` runs 19 tests covering models, JSON round-trip (including old/corrupted files), CRUD, search, combined filters, sorting in both directions and tag handling.

## 6. Challenges & Considerations
* Sorting across different task types (solved by keeping tasks without the field at the end).
* Keeping the CLI simple as options grow – filters use "press Enter to skip".
* Displaying Thai text in the Windows terminal – stdout is set to UTF-8 (`chcp 65001` may also be needed).

## 7. Future Enhancements
Reminders for tasks due soon on start-up · editing a task's description/tags · recurring tasks · SQLite instead of JSON (only `data_persistence.py` would change) · a Tkinter GUI that reuses `task_manager.py` unchanged.
