# enhanced-task-manager-design/src/cli_interface.py
"""
User Interface Layer - every input() and print() lives here.
No business logic: it only validates input and calls TaskManager.
"""
import datetime

from .task import DATE_FORMAT, PRIORITIES
from .task_manager import SORT_CRITERIA

LINE = "=" * 48
THIN = "-" * 48


class CLIInterface:
    def __init__(self, task_manager, owner_name="", owner_id=""):
        self.manager = task_manager
        self.owner_name = owner_name
        self.owner_id = owner_id
        self.actions = {
            '1': self.add_normal_task,
            '2': self.add_due_date_task,
            '3': self.add_priority_task,
            '4': self.list_tasks,
            '5': self.complete_task,
            '6': self.delete_task,
            '7': self.search_tasks,
            '8': self.filter_tasks,
            '9': self.sort_tasks,
        }

    # ---------- display ----------
    def show_banner(self):
        print(LINE)
        print("   Enhanced Task Manager (Week 11)")
        if self.owner_name:
            print(f"   {self.owner_name} | {self.owner_id}")
        print(LINE)

    def display_menu(self):
        s = self.manager.summary()
        print(f"\n{LINE}")
        print("        Enhanced Task Manager (Week 11)")
        print(f"   งานทั้งหมด {s['total']} | เสร็จ {s['completed']} | ค้าง {s['pending']} | เลยกำหนด {s['overdue']}")
        print(LINE)
        print("1. เพิ่มงานทั่วไป (Add Normal Task)")
        print("2. เพิ่มงานที่มีวันครบกำหนด (Add Due Date Task)")
        print("3. เพิ่มงานที่มีระดับความสำคัญ (Add Priority Task)")
        print("4. แสดงรายการงานทั้งหมด (List All Tasks)")
        print("5. เปลี่ยนสถานะงานเป็นเสร็จสิ้น (Complete Task)")
        print("6. ลบงาน (Delete Task)")
        print("7. ค้นหางาน (Search Tasks)")
        print("8. กรองงาน (Filter Tasks)")
        print("9. เรียงลำดับงาน (Sort Tasks)")
        print("0. ออกจากโปรแกรม (Exit)")
        print(THIN)

    @staticmethod
    def display_tasks(tasks, title):
        print(f"\n--- {title} ({len(tasks)} รายการ) ---")
        if not tasks:
            print("  (ไม่พบงาน)")
        for task in tasks:
            print(f"- {task}")
        print(THIN)

    # ---------- input helpers ----------
    @staticmethod
    def ask(prompt):
        return input(prompt).strip()

    def ask_description(self):
        while True:
            text = self.ask("กรอกรายละเอียดงาน (Description): ")
            if text:
                return text
            print("[ข้อผิดพลาด] รายละเอียดงานต้องไม่เป็นค่าว่าง กรุณาลองใหม่")

    def ask_date(self, prompt, allow_blank=False):
        while True:
            text = self.ask(prompt)
            if not text and allow_blank:
                return None
            try:
                return datetime.datetime.strptime(text, DATE_FORMAT).date()
            except ValueError:
                print("[ข้อผิดพลาด] รูปแบบวันที่ต้องเป็น YYYY-MM-DD เช่น 2026-12-31")

    def ask_priority(self, allow_blank=False):
        while True:
            text = self.ask("กรอกระดับความสำคัญ (High/Medium/Low"
                            + (", เว้นว่าง = ทั้งหมด" if allow_blank else "") + "): ").capitalize()
            if not text and allow_blank:
                return None
            if text in PRIORITIES:
                return text
            print("[ข้อผิดพลาด] กรุณาใส่ High, Medium หรือ Low")

    def ask_tags(self, prompt="กรอกป้ายกำกับ (คั่นด้วยจุลภาค เช่น study,python - เว้นว่างได้): "):
        return [t.strip().lower() for t in self.ask(prompt).split(',') if t.strip()]

    def ask_task_id(self, prompt):
        text = self.ask(prompt)
        try:
            return int(text)
        except ValueError:
            print(f"[ข้อผิดพลาด] '{text}' ไม่ใช่ตัวเลข กรุณาใส่ ID เป็นตัวเลข")
            return None

    def ask_yes_no(self, prompt, allow_blank=True):
        while True:
            text = self.ask(prompt).lower()
            if text in ('y', 'yes'):
                return True
            if text in ('n', 'no'):
                return False
            if not text and allow_blank:
                return None
            print("[ข้อผิดพลาด] กรุณาตอบ y หรือ n")

    # ---------- menu actions ----------
    def add_normal_task(self):
        task = self.manager.add_normal_task(self.ask_description(), tags=self.ask_tags())
        print(f"[สำเร็จ] เพิ่มงานทั่วไป ID {task.id} เรียบร้อยแล้ว")

    def add_due_date_task(self):
        description = self.ask_description()
        due = self.ask_date("กรอกวันครบกำหนด (YYYY-MM-DD เช่น 2026-12-31): ")
        task = self.manager.add_due_date_task(description, due, tags=self.ask_tags())
        print(f"[สำเร็จ] เพิ่มงาน ID {task.id} (ครบกำหนด {due}) เรียบร้อยแล้ว")

    def add_priority_task(self):
        description = self.ask_description()
        priority = self.ask_priority()
        task = self.manager.add_priority_task(description, priority, tags=self.ask_tags())
        print(f"[สำเร็จ] เพิ่มงาน ID {task.id} (ความสำคัญ {priority}) เรียบร้อยแล้ว")

    def list_tasks(self):
        self.display_tasks(self.manager.get_all_tasks(), "รายการงานทั้งหมด")

    def complete_task(self):
        task_id = self.ask_task_id("กรอก ID งานที่ทำเสร็จแล้ว: ")
        if task_id is not None:
            ok, msg = self.manager.complete_task(task_id)
            print(("[สำเร็จ] " if ok else "[แจ้งเตือน] ") + msg)

    def delete_task(self):
        task_id = self.ask_task_id("กรอก ID งานที่ต้องการลบ: ")
        if task_id is None:
            return
        task = self.manager.get_task_by_id(task_id)
        if task is None:
            print(f"[แจ้งเตือน] ไม่พบงาน ID {task_id}")
            return
        if self.ask_yes_no(f"ยืนยันลบงาน '{task.description}'? (y/n): ", allow_blank=False):
            ok, msg = self.manager.delete_task(task_id)
            print("[สำเร็จ] " + msg)
        else:
            print("[แจ้งเตือน] ยกเลิกการลบ")

    def search_tasks(self):
        keyword = self.ask("กรอกคำค้นหา (ค้นทั้งรายละเอียดและป้ายกำกับ): ")
        if not keyword:
            print("[ข้อผิดพลาด] คำค้นหาต้องไม่เป็นค่าว่าง")
            return
        self.display_tasks(self.manager.search_tasks(keyword), f"ผลการค้นหา '{keyword}'")

    def filter_tasks(self):
        print("\n--- กรองงาน (กด Enter เพื่อข้ามเงื่อนไขนั้น) ---")
        status = self.ask_yes_no("เฉพาะงานที่เสร็จแล้ว? (y = เสร็จ / n = ยังไม่เสร็จ): ")
        before = self.ask_date("ครบกำหนดภายในวันที่ (YYYY-MM-DD): ", allow_blank=True)
        after = self.ask_date("ครบกำหนดตั้งแต่วันที่ (YYYY-MM-DD): ", allow_blank=True)
        priority = self.ask_priority(allow_blank=True)
        tags = self.ask_tags("ต้องมีป้ายกำกับทั้งหมดนี้ (คั่นด้วยจุลภาค): ")
        results = self.manager.filter_tasks(status=status, due_date_before=before, due_date_after=after,
                                            priority_level=priority, contains_tags=tags or None)
        self.display_tasks(results, "ผลการกรองงาน")

    def sort_tasks(self):
        print(f"\nเกณฑ์ที่เลือกได้: {', '.join(SORT_CRITERIA)}")
        criterion = self.ask("เรียงตาม (Enter = id): ").lower() or "id"
        if criterion not in SORT_CRITERIA:
            print(f"[ข้อผิดพลาด] ไม่รู้จักเกณฑ์ '{criterion}'")
            return
        reverse = bool(self.ask_yes_no("เรียงจากมากไปน้อย? (y/n, Enter = n): "))
        tasks = self.manager.sort_tasks(criterion, reverse)
        self.display_tasks(tasks, f"เรียงตาม {criterion} ({'มากไปน้อย' if reverse else 'น้อยไปมาก'})")

    # ---------- main loop ----------
    def run(self):
        self.show_banner()
        while True:
            self.display_menu()
            try:
                choice = self.ask("เลือกเมนู (0-9): ")
                if choice == '0':
                    print("ออกจากโปรแกรม ข้อมูลถูกบันทึกแล้ว ขอบคุณค่ะ")
                    break
                action = self.actions.get(choice)
                if action:
                    action()
                else:
                    print("[ข้อผิดพลาด] กรุณาเลือกเมนู 0-9")
            except (KeyboardInterrupt, EOFError):
                print("\nออกจากโปรแกรม ข้อมูลถูกบันทึกแล้ว ขอบคุณค่ะ")
                break
