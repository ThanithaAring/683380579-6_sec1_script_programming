# My API Data Fetcher CLI (Week 10)

**ผู้จัดทำ:** นางสาวธนิษฐา อภิรัตน์มนตรี  
**รหัสนักศึกษา:** 683380579-6

A command-line app that fetches JSON data from the free [JSONPlaceholder](https://jsonplaceholder.typicode.com/) REST API using the `requests` library, then processes and displays it.

## Features

| Menu | Endpoint | What it shows |
|---|---|---|
| 1. Fetch a Single TODO Item | `GET /todos/{id}` | ID, user, title, status and the raw JSON |
| 2. Fetch All Posts | `GET /posts` | Table of the first N posts (you choose N, default 5), total count, number of authors |
| 3. Fetch TODOs by User ID | `GET /todos?userId={id}` + `GET /users/{id}` | The user's name, all their TODOs as a checklist, and a completion summary with a progress bar |
| 4. Exit | | |

Extras:
* Options 2 and 3 can **save the result to `output/*.json`**.
* Input is validated – letters, 0 or negative numbers are rejected and asked again.
* Error handling for **404**, other HTTP errors, **no internet**, **timeout** and **invalid JSON**, each with a clear Thai message.
* A `requests.Session` reuses the connection, and query strings are passed with `params=`.

## How to Run

```powershell
py -m venv .venv
.venv\Scripts\activate          # macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
python main.py
```

### Tests (offline – HTTP is mocked)
```powershell
python -m unittest discover tests -v
```

## Project Structure

```
my-api-fetcher/
├── src/
│   ├── __init__.py
│   └── api_client.py     # APIClient (GET + error handling) and helper functions
├── tests/
│   └── test_api_client.py
├── output/               # JSON files saved from the CLI
├── screenshots/
├── main.py               # CLI menu
├── requirements.txt
├── .gitignore
└── README.md
```

## Screenshots

### 1. Fetch a Single TODO Item
![Fetch single TODO](screenshots/1_single_todo.png)

### 2. Fetch All Posts
![Fetch all posts](screenshots/2_all_posts.png)

### 3. Fetch TODOs by User ID
![Fetch user TODOs](screenshots/3_user_todos.png)

## Extension Ideas
* Fetch comments, albums and photos; show the comments of a chosen post
* Filter TODOs by status with `?completed=true`
* Export results to CSV
