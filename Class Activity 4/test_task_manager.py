# enhanced-task-manager-design/tests/test_task_manager.py
"""Unit tests. Run with: python -m unittest discover tests -v"""
import datetime
import json
import os
import tempfile
import unittest

from src.task import Task, DueDateTask, PriorityTask
from src.task_manager import TaskManager


class TempManagerMixin:
    """Gives each test a TaskManager backed by its own temporary JSON file."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = os.path.join(self.tmp.name, "tasks.json")
        self.m = TaskManager(self.path)

    def tearDown(self):
        self.tmp.cleanup()


class TestTaskModels(unittest.TestCase):
    def test_tags_are_normalized_and_unique(self):
        t = Task(1, "x", tags=[" Study ", "study", "", "GitHub"])
        self.assertEqual(t.tags, ["study", "github"])

    def test_remove_tag(self):
        t = Task(1, "x", tags=["a", "b"])
        self.assertTrue(t.remove_tag(" A "))
        self.assertFalse(t.remove_tag("zzz"))
        self.assertEqual(t.tags, ["b"])

    def test_due_date_parsing_and_validation(self):
        self.assertEqual(DueDateTask(1, "x", "2026-10-20").due_date, datetime.date(2026, 10, 20))
        with self.assertRaises(ValueError):
            DueDateTask(1, "x", "20/10/2026")

    def test_priority_validation(self):
        self.assertEqual(PriorityTask(1, "x", "high").priority, "High")
        with self.assertRaises(ValueError):
            PriorityTask(1, "x", "Urgent")

    def test_str_order(self):
        t = DueDateTask(1, "Report", "2999-01-01", tags=["study"])
        self.assertEqual(str(t), "ID: 1 | Description: Report | Status: Pending | Due: 2999-01-01 | Tags: study")

    def test_overdue(self):
        t = DueDateTask(1, "x", "2026-01-01")
        self.assertTrue(t.is_overdue(datetime.date(2026, 1, 2)))
        t.mark_complete()
        self.assertFalse(t.is_overdue(datetime.date(2026, 1, 2)))


class TestPersistence(TempManagerMixin, unittest.TestCase):
    def test_round_trip_keeps_types_and_thai_text(self):
        self.m.add_normal_task("งานทดสอบ", ["ไทย"])
        self.m.add_due_date_task("due", "2026-12-31", ["a"])
        self.m.add_priority_task("prio", "Low")
        reloaded = TaskManager(self.path).tasks
        self.assertEqual([type(t).__name__ for t in reloaded], ["Task", "DueDateTask", "PriorityTask"])
        self.assertEqual(reloaded[0].description, "งานทดสอบ")
        self.assertEqual(reloaded[0].tags, ["ไทย"])

    def test_old_file_without_tags(self):
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump([{"id": 5, "description": "old", "completed": False, "_type": "Task"}], f)
        m = TaskManager(self.path)
        self.assertEqual(m.tasks[0].tags, [])
        self.assertEqual(m.next_id, 6)

    def test_corrupted_file(self):
        with open(self.path, "w", encoding="utf-8") as f:
            f.write("{ not json")
        self.assertEqual(TaskManager(self.path).tasks, [])


class TestManagerOperations(TempManagerMixin, unittest.TestCase):
    def setUp(self):
        super().setUp()
        self.m.add_normal_task("Buy pens", ["personal"])                               # 1
        self.m.add_due_date_task("Math homework", "2026-10-16", ["study", "math"])      # 2
        self.m.add_due_date_task("Push to GitHub", "2026-10-20", ["study", "github"])   # 3
        self.m.add_priority_task("Final project", "High", ["study", "python"])         # 4
        self.m.add_priority_task("Stats practice", "Low", ["study"])                   # 5
        self.m.add_priority_task("Slides", "Medium", ["presentation"])                 # 6
        self.m.complete_task(2)

    def test_ids_are_unique_after_delete(self):
        self.m.delete_task(6)
        self.assertEqual(self.m.add_normal_task("new").id, 7)

    def test_complete_messages(self):
        self.assertFalse(self.m.complete_task(2)[0])     # already done
        self.assertFalse(self.m.complete_task(99)[0])    # not found
        self.assertTrue(self.m.complete_task(1)[0])

    def test_invalid_inputs_return_none(self):
        self.assertIsNone(self.m.add_due_date_task("x", "2026-13-40"))
        self.assertIsNone(self.m.add_priority_task("x", "Urgent"))
        self.assertEqual(len(self.m.tasks), 6)

    def test_search_partial_case_insensitive(self):
        self.assertEqual([t.id for t in self.m.search_tasks("GIT")], [3])
        self.assertEqual([t.id for t in self.m.search_tasks("stud")], [2, 3, 4, 5])
        self.assertEqual(self.m.search_tasks("   "), [])

    def test_filter_single_and_combined(self):
        self.assertEqual([t.id for t in self.m.filter_tasks(status=True)], [2])
        self.assertEqual([t.id for t in self.m.filter_tasks(priority_level="high")], [4])
        self.assertEqual([t.id for t in self.m.filter_tasks(
            due_date_before=datetime.date(2026, 10, 20), due_date_after=datetime.date(2026, 10, 17))], [3])
        self.assertEqual([t.id for t in self.m.filter_tasks(status=False, contains_tags=["STUDY"])], [3, 4, 5])
        self.assertEqual(self.m.filter_tasks(contains_tags=["study", "presentation"]), [])

    def test_sort_priority_others_last(self):
        self.assertEqual([t.id for t in self.m.sort_tasks("priority")], [4, 6, 5, 1, 2, 3])
        self.assertEqual([t.id for t in self.m.sort_tasks("priority", reverse=True)], [5, 6, 4, 1, 2, 3])

    def test_sort_due_date_others_last(self):
        self.assertEqual([t.id for t in self.m.sort_tasks("due_date")], [2, 3, 1, 4, 5, 6])
        self.assertEqual([t.id for t in self.m.sort_tasks("due_date", reverse=True)], [3, 2, 1, 4, 5, 6])

    def test_sort_other_criteria(self):
        self.assertEqual([t.id for t in self.m.sort_tasks("id", reverse=True)], [6, 5, 4, 3, 2, 1])
        self.assertEqual(self.m.sort_tasks("description")[0].description, "Buy pens")
        self.assertEqual(self.m.sort_tasks("completed")[-1].id, 2)
        with self.assertRaises(ValueError):
            self.m.sort_tasks("color")

    def test_tag_management(self):
        self.assertTrue(self.m.add_tag_to_task(1, "Urgent")[0])
        self.assertFalse(self.m.add_tag_to_task(1, "urgent")[0])
        self.assertTrue(self.m.remove_tag_from_task(1, "urgent")[0])
        self.assertFalse(self.m.remove_tag_from_task(1, "urgent")[0])

    def test_summary(self):
        s = self.m.summary()
        self.assertEqual((s["total"], s["completed"], s["pending"]), (6, 1, 5))


if __name__ == "__main__":
    unittest.main()
