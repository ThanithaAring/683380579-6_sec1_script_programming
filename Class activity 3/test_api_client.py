# my-api-fetcher/tests/test_api_client.py
"""Offline tests - the HTTP layer is mocked. Run: python -m unittest discover tests -v"""
import io
import unittest
from contextlib import redirect_stdout
from unittest.mock import MagicMock, patch

import requests

import main
from src.api_client import APIClient, summarize_todos, shorten

TODO_1 = {"userId": 1, "id": 1, "title": "delectus aut autem", "completed": False}
POSTS = [{"userId": (i - 1) // 10 + 1, "id": i, "title": f"post {i}", "body": "line1\nline2"} for i in range(1, 101)]
USER_TODOS = [{"userId": 2, "id": 21, "title": "a", "completed": True},
              {"userId": 2, "id": 22, "title": "b", "completed": False},
              {"userId": 2, "id": 23, "title": "c", "completed": True}]


def fake_response(status=200, data=None, bad_json=False):
    resp = MagicMock()
    resp.status_code = status
    if status >= 400:
        resp.raise_for_status.side_effect = requests.exceptions.HTTPError(f"{status} error")
    if bad_json:
        resp.json.side_effect = ValueError("no json")
    else:
        resp.json.return_value = data
    return resp


class TestAPIClient(unittest.TestCase):
    def setUp(self):
        self.client = APIClient()
        self.client.session = MagicMock()

    def call(self, fn, *args):
        with redirect_stdout(io.StringIO()):
            return fn(*args)

    def test_single_todo(self):
        self.client.session.get.return_value = fake_response(data=TODO_1)
        self.assertEqual(self.call(self.client.fetch_single_todo, 1), TODO_1)
        self.client.session.get.assert_called_with(
            "https://jsonplaceholder.typicode.com/todos/1", params=None, timeout=10)

    def test_user_todos_uses_query_params(self):
        self.client.session.get.return_value = fake_response(data=USER_TODOS)
        self.assertEqual(len(self.call(self.client.fetch_user_todos, 2)), 3)
        self.client.session.get.assert_called_with(
            "https://jsonplaceholder.typicode.com/todos", params={"userId": 2}, timeout=10)

    def test_404(self):
        self.client.session.get.return_value = fake_response(status=404)
        self.assertIsNone(self.call(self.client.fetch_single_todo, 99999))
        self.assertIn("404", self.client.last_error)

    def test_server_error(self):
        self.client.session.get.return_value = fake_response(status=500)
        self.assertIsNone(self.call(self.client.fetch_all_posts))
        self.assertIn("500", self.client.last_error)

    def test_connection_error_and_timeout(self):
        self.client.session.get.side_effect = requests.exceptions.ConnectionError()
        self.assertIsNone(self.call(self.client.fetch_all_posts))
        self.assertIn("อินเทอร์เน็ต", self.client.last_error)
        self.client.session.get.side_effect = requests.exceptions.Timeout()
        self.assertIsNone(self.call(self.client.fetch_all_posts))
        self.assertIn("Timeout", self.client.last_error)

    def test_bad_json(self):
        self.client.session.get.return_value = fake_response(bad_json=True)
        self.assertIsNone(self.call(self.client.fetch_all_posts))
        self.assertIn("JSON", self.client.last_error)


class TestHelpers(unittest.TestCase):
    def test_summarize(self):
        self.assertEqual(summarize_todos(USER_TODOS), {"total": 3, "completed": 2, "pending": 1, "percent": 66.7})
        self.assertEqual(summarize_todos([])["percent"], 0.0)

    def test_shorten(self):
        self.assertEqual(shorten("a\nb  c", 20), "a b c")
        self.assertEqual(shorten("abcdefghij", 8), "abcde...")


class TestCLI(unittest.TestCase):
    """Drives the three required menu options with typed input and a fake client."""

    def setUp(self):
        self.client = MagicMock()
        self.client.fetch_single_todo.return_value = TODO_1
        self.client.fetch_all_posts.return_value = POSTS
        self.client.fetch_user_todos.return_value = USER_TODOS
        self.client.fetch_user.return_value = {"name": "Ervin Howell"}

    def run_cli(self, fn, inputs):
        out = io.StringIO()
        with patch("builtins.input", side_effect=inputs), redirect_stdout(out):
            fn(self.client)
        return out.getvalue()

    def test_option1_with_invalid_then_valid_input(self):
        out = self.run_cli(main.fetch_single_todo, ["abc", "0", "1"])
        self.assertIn("ไม่ใช่ตัวเลข", out)
        self.assertIn("delectus aut autem", out)
        self.assertIn("Pending", out)

    def test_option2_default_limit(self):
        out = self.run_cli(main.fetch_all_posts, ["", "n"])
        self.assertIn("แสดง 5 จาก 100", out)
        self.assertIn("และอีก 95 โพสต์", out)

    def test_option3_summary(self):
        out = self.run_cli(main.fetch_user_todos, ["2", "n"])
        self.assertIn("User ID 2 - Ervin Howell", out)
        self.assertIn("ทั้งหมด 3 | เสร็จ 2 | ค้าง 1", out)

    def test_option3_unknown_user(self):
        self.client.fetch_user_todos.return_value = []
        out = self.run_cli(main.fetch_user_todos, ["99"])
        self.assertIn("ไม่พบ TODO", out)


if __name__ == "__main__":
    unittest.main()
