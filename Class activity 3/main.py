# my-api-fetcher/main.py
"""
Week 10 - Interacting with Web APIs: Fetching and Processing JSON Data
Interactive CLI that fetches data from JSONPlaceholder with the requests library.
"""
import datetime
import json
import os
import sys

from src.api_client import APIClient, summarize_todos, shorten

STUDENT_NAME = "นางสาวธนิษฐา อภิรัตน์มนตรี"
STUDENT_ID = "683380579-6"

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")
LINE = "=" * 64
THIN = "-" * 64


# ---------- input helpers ----------
def ask_positive_int(prompt, default=None):
    """Asks until the user types a positive whole number (or Enter for the default)."""
    while True:
        raw = input(prompt).strip()
        if not raw and default is not None:
            return default
        try:
            value = int(raw)
            if value > 0:
                return value
            print("[ERROR] กรุณาใส่ตัวเลขที่มากกว่า 0")
        except ValueError:
            print(f"[ERROR] '{raw}' ไม่ใช่ตัวเลขจำนวนเต็ม กรุณาลองใหม่")


def ask_yes_no(prompt):
    return input(prompt).strip().lower() in ("y", "yes")


def save_json(data, name):
    """Saves fetched data to output/<name>_<timestamp>.json and returns the path."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    path = os.path.join(OUTPUT_DIR, f"{name}_{datetime.datetime.now():%Y%m%d_%H%M%S}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    return path


def offer_save(data, name):
    if ask_yes_no("บันทึกผลลัพธ์เป็นไฟล์ JSON หรือไม่? (y/n): "):
        print(f"[SAVED] {save_json(data, name)}")


# ---------- menu actions ----------
def fetch_single_todo(client):
    todo_id = ask_positive_int("ใส่ TODO ID (1-200): ")
    todo = client.fetch_single_todo(todo_id)
    if todo is None:
        return
    status = "เสร็จแล้ว (Completed)" if todo.get("completed") else "ยังไม่เสร็จ (Pending)"
    print(f"\n--- 1. TODO Item #{todo.get('id')} ---")
    print(f"  TODO ID   : {todo.get('id')}")
    print(f"  User ID   : {todo.get('userId')}")
    print(f"  Title     : {todo.get('title')}")
    print(f"  Status    : {status}")
    print(f"  Raw JSON  : {json.dumps(todo, ensure_ascii=False)}")
    print(THIN)


def fetch_all_posts(client):
    posts = client.fetch_all_posts()
    if posts is None:
        return
    total = len(posts)
    limit = ask_positive_int(f"ได้รับโพสต์ทั้งหมด {total} รายการ ต้องการแสดงกี่รายการ? (Enter = 5): ", default=5)
    limit = min(limit, total)

    authors = {p.get("userId") for p in posts}
    print(f"\n--- 2. All Posts: แสดง {limit} จาก {total} รายการ (ผู้เขียน {len(authors)} คน) ---")
    print(f"{'ID':>4} | {'User':>4} | {'Title':<40} | Body")
    print(THIN)
    for post in posts[:limit]:
        print(f"{post.get('id'):>4} | {post.get('userId'):>4} | {shorten(post.get('title'), 40):<40} | "
              f"{shorten(post.get('body'), 30)}")
    if total > limit:
        print(f"... และอีก {total - limit} โพสต์ที่ไม่ได้แสดง")
    print(THIN)
    offer_save(posts[:limit], "posts")


def fetch_user_todos(client):
    user_id = ask_positive_int("ใส่ User ID (1-10): ")
    todos = client.fetch_user_todos(user_id)
    if todos is None:
        return
    if not todos:
        print(f"[INFO] ไม่พบ TODO ของ User ID {user_id} (JSONPlaceholder มีผู้ใช้ ID 1-10)")
        return

    user = client.fetch_user(user_id) or {}
    s = summarize_todos(todos)
    name = f" - {user.get('name')}" if user.get("name") else ""
    print(f"\n--- 3. TODOs of User ID {user_id}{name} ---")
    print(f"{'ID':>4} | {'Status':<9} | Title")
    print(THIN)
    for todo in todos:
        mark = "[x] Done" if todo.get("completed") else "[ ] Todo"
        print(f"{todo.get('id'):>4} | {mark:<9} | {shorten(todo.get('title'), 46)}")
    print(THIN)
    bar = "#" * int(s["percent"] // 5) + "." * (20 - int(s["percent"] // 5))
    print(f"สรุป: ทั้งหมด {s['total']} | เสร็จ {s['completed']} | ค้าง {s['pending']} | [{bar}] {s['percent']}%")
    print(THIN)
    offer_save({"user_id": user_id, "summary": s, "todos": todos}, f"user{user_id}_todos")


# ---------- main loop ----------
def show_banner():
    print(LINE)
    print("   Web API Data Fetcher (Week 10)  -  JSONPlaceholder")
    print(f"   {STUDENT_NAME}  |  {STUDENT_ID}")
    print(LINE)


def display_menu():
    print("\n--- API Data Fetcher Menu ---")
    print("  1. Fetch a Single TODO Item   (ดึง TODO รายการเดียว)")
    print("  2. Fetch All Posts            (ดึงโพสต์ทั้งหมด)")
    print("  3. Fetch TODOs by User ID     (ดึง TODO ตามผู้ใช้)")
    print("  4. Exit                       (ออกจากโปรแกรม)")
    print(THIN)


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    client = APIClient()
    actions = {"1": fetch_single_todo, "2": fetch_all_posts, "3": fetch_user_todos}
    show_banner()
    while True:
        display_menu()
        try:
            choice = input("เลือกเมนู (1-4): ").strip()
            if choice == "4":
                print("ออกจากโปรแกรม ขอบคุณค่ะ")
                break
            if choice in actions:
                actions[choice](client)
            else:
                print("[ERROR] กรุณาเลือก 1, 2, 3 หรือ 4")
        except (KeyboardInterrupt, EOFError):
            print("\nออกจากโปรแกรม ขอบคุณค่ะ")
            break


if __name__ == "__main__":
    main()
