# my-oop-task-manager/tests/test_oop.py
"""Run: python -m unittest discover tests -v"""
import io
import os
import tempfile
import unittest
from contextlib import redirect_stdout

from src.task import Task
from src.task_manager import TaskManager


class TestTask(unittest.TestCase):
    def test_init_and_mark_complete(self):
        t = Task(1, "Read")
        self.assertFalse(t.completed)
        t.mark_complete()
        self.assertTrue(t.completed)

    def test_dict_round_trip(self):
        t = Task(3, "อ่านหนังสือ", True)
        self.assertEqual(repr(Task.from_dict(t.to_dict())), repr(t))

    def test_str(self):
        self.assertEqual(str(Task(2, "B")), "ID: 2 | Description: B | Status: PENDING")
        self.assertIn("COMPLETED", str(Task(2, "B", True)))


class TestTaskManager(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = os.path.join(self.tmp.name, "tasks.json")   # absolute path -> not the real data file

    def tearDown(self):
        self.tmp.cleanup()

    def manager(self):
        with redirect_stdout(io.StringIO()):
            return TaskManager(self.path)

    def quiet(self, fn, *args):
        out = io.StringIO()
        with redirect_stdout(out):
            result = fn(*args)
        return result, out.getvalue()

    def test_add_complete_list_persist(self):
        m = self.manager()
        self.quiet(m.add_task, "Task A")
        self.quiet(m.add_task, "Task B")
        self.quiet(m.complete_task, 1)
        _, out = self.quiet(m.list_tasks)
        self.assertIn("ID: 1 | Description: Task A | Status: COMPLETED", out)
        self.assertIn("ID: 2 | Description: Task B | Status: PENDING", out)

        reloaded = self.manager()                                # new object reads the same file
        self.assertEqual([t.completed for t in reloaded.tasks], [True, False])
        self.assertEqual(reloaded.next_id, 3)

    def test_errors(self):
        m = self.manager()
        self.assertIsNone(self.quiet(m.add_task, "   ")[0])
        self.assertFalse(self.quiet(m.complete_task, 99)[0])
        self.assertFalse(self.quiet(m.delete_task, 99)[0])
        self.quiet(m.add_task, "x")
        self.quiet(m.complete_task, 1)
        self.assertFalse(self.quiet(m.complete_task, 1)[0])     # already completed

    def test_delete_keeps_ids_unique(self):
        m = self.manager()
        self.quiet(m.add_task, "a")
        self.quiet(m.add_task, "b")
        self.quiet(m.delete_task, 2)
        # next_id keeps counting up, so a deleted ID is never handed out again
        self.assertEqual(self.quiet(m.add_task, "c")[0].id, 3)
        self.quiet(m.delete_task, 1)
        self.assertEqual(self.quiet(m.add_task, "d")[0].id, 4)

    def test_corrupted_file(self):
        with open(self.path, "w") as f:
            f.write("not json")
        self.assertEqual(self.manager().tasks, [])


if __name__ == "__main__":
    unittest.main()
